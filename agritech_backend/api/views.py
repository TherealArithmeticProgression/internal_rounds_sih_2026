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
from risk_engine.risk_score_generator import calculate_risk_score
from django.shortcuts import get_object_or_404
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


class FarmViewSet(viewsets.ModelViewSet):
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer


class SensorNodeViewSet(viewsets.ModelViewSet):
    queryset = SensorNode.objects.all()
    serializer_class = SensorNodeSerializer


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all()
    serializer_class = SensorReadingSerializer


class TreatmentRecommendationViewSet(viewsets.ModelViewSet):
    queryset = TreatmentRecommendation.objects.all()
    serializer_class = TreatmentRecommendationSerializer


class DiseasePredictionViewSet(viewsets.ModelViewSet):
    queryset = DiseasePrediction.objects.all()
    serializer_class = DiseasePredictionSerializer

@extend_schema(
    request={
        "multipart/form-data": PredictSerializer
    }
)
class PredictView(views.APIView):
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
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer

class RiskScoreView(views.APIView):
    def get(self, request, farm_id, disease):

        latest_reading = SensorReading.objects.filter(
            sensor_node__farm_id=farm_id
        ).order_by("-recorded_at").first()

        if not latest_reading:
            return response.Response(
                {"error": "No sensor readings found for this farm."},
                status=status.HTTP_404_NOT_FOUND
            )

        input_details = {
            "temp_min": latest_reading.temperature,
            "temp_max": latest_reading.temperature,
            "rh_morning": latest_reading.humidity,
            "rh_evening": latest_reading.humidity,
            "soil_moisture": latest_reading.soil_moisture,
        }

        try:
            result = calculate_risk_score(
                disease,
                input_details
            )

        except ValueError as e:
            return response.Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return response.Response({
            "farm_id": farm_id,
            "disease": result["disease"],
            "score": result["risk_score"],
            "band": result["risk_band"],
            "advisory": result.get("agronomic_advisory"),
        })