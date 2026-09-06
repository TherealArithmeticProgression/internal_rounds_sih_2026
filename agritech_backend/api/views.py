import base64
from django.core.files.base import ContentFile
from rest_framework import views, response, status , viewsets
from drf_spectacular.utils import extend_schema
import numpy as np
import onnxruntime as ort
from PIL import Image
import io
import os
from django.conf import settings
from risk_engine.tomato_risk_engine import Disease, SensorReading as TomatoSensorReading, calculate_all_risks, calculate_risk
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import (
    Farm,
    SensorNode,
    SensorReading,
    TreatmentRecommendation,
    DiseasePrediction,
    RiskScore,
)

from .serializers import (
    FarmSerializer,
    SensorNodeSerializer,
    SensorReadingSerializer,
    TreatmentRecommendationSerializer,
    DiseasePredictionSerializer,
    RiskScoreSerializer,
    PredictSerializer,
)


from rest_framework.permissions import IsAuthenticated

class FarmViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmSerializer

    def get_queryset(self):
        return Farm.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SensorNodeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SensorNodeSerializer

    def get_queryset(self):
        return SensorNode.objects.filter(farm__user=self.request.user)


class SensorReadingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        return SensorReading.objects.filter(sensor_node__farm__user=self.request.user)


class TreatmentRecommendationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TreatmentRecommendation.objects.all()
    serializer_class = TreatmentRecommendationSerializer

    http_method_names = ["get", "head", "options"]



class DiseasePredictionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DiseasePredictionSerializer

    def get_queryset(self):
        return DiseasePrediction.objects.filter(farm__user=self.request.user)

@extend_schema(
    request={
        "multipart/form-data": PredictSerializer
    }
)
class PredictView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        image_data = request.data.get("image")

        if not image_data:
            return response.Response(
                {"error": "Image is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            format, imgstr = image_data.split(";base64,")
            image_bytes = base64.b64decode(imgstr)

            # Convert image to model input
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image = image.resize((224, 224))

            image_array = np.array(image, dtype=np.float32) / 255.0
            image_array = np.transpose(image_array, (2, 0, 1))
            image_array = np.expand_dims(image_array, axis=0)

            # Load ONNX model
            model_path = os.path.join(
                settings.BASE_DIR.parent,
                "weights",
                "weights_final_.onnx"
            )

            session = ort.InferenceSession(model_path)

            input_name = session.get_inputs()[0].name
            output = session.run(
                None,
                {input_name: image_array}
            )[0][0]

            predicted_index = int(np.argmax(output))

            class_names = {
                0: "bacterial_spot",
                1: "early_blight",
                2: "late_blight",
                3: "septoria_leaf_spot",
            }

            predicted_label = class_names[predicted_index]

            return response.Response({
                "predicted_label": predicted_label,
                "predicted_index": predicted_index,
                "raw_output": output.tolist(),
            })

        except Exception as e:
            return response.Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class RiskScoreViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RiskScoreSerializer

    def get_queryset(self):
        return RiskScore.objects.filter(farm__user=self.request.user)

class RiskScoreView(views.APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, farm_id, disease):

        get_object_or_404(Farm, id=farm_id, user=request.user)

        readings = SensorReading.objects.filter(sensor_node__farm_id=farm_id, recorded_at__gte=timezone.now() - timedelta(days=7)).order_by("recorded_at")
        samples = [
            TomatoSensorReading(timestamp=row.recorded_at, temp_c=row.temperature, humidity_pct=row.humidity, rainfall_mm=row.rainfall_mm, soil_moisture_pct=row.soil_moisture or 0)
            for row in readings if row.temperature is not None and row.humidity is not None
        ]
        if not samples:
            return response.Response(
                {"error": "No usable temperature and humidity readings found for this farm in the last 7 days."},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            if disease == "all":
                results = calculate_all_risks(samples)
                return response.Response({"farm_id": farm_id, "window_hours": 168, "estimated_leaf_wetness": True, "risks": [{"disease": key.value, "score": value.score, "band": value.band.value, "explanation": value.explanation, "contributing_factors": value.contributing_factors} for key, value in results.items()]})
            result = calculate_risk(Disease(disease), samples)
        except ValueError:
            return response.Response(
                {"error": "Unknown tomato disease risk type."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response({
            "farm_id": farm_id,
            "window_hours": 168,
            "estimated_leaf_wetness": True,
            "disease": result.disease.value,
            "score": result.score,
            "band": result.band.value,
            "explanation": result.explanation,
            "contributing_factors": result.contributing_factors,
        })
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

class DiseaseOutbreakView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        recent_date = timezone.now() - timedelta(days=7)
        outbreaks = DiseasePrediction.objects.filter(
            predicted_at__gte=recent_date, 
            confidence__gte=0.8
        ).values('predicted_label').annotate(count=Count('id')).order_by('-count')
        
        return response.Response({
            "outbreaks": list(outbreaks),
            "message": "Outbreak data retrieved successfully"
        })
