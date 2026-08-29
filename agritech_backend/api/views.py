import base64
from django.core.files.base import ContentFile
from rest_framework import views, response, status , viewsets
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
            ext = format.split("/")[-1]

            image_file = ContentFile(
                base64.b64decode(imgstr),
                name=f"prediction.{ext}"
            )

            return response.Response({
                "message": "Image received successfully.",
                "format": ext
            })

        except Exception:
            return response.Response(
                {"error": "Invalid Base64 image."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class RiskScoreViewSet(viewsets.ModelViewSet):
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer

class RiskScoreView(views.APIView):
    def get(self, request, farm_id, disease):
        risk_score = RiskScore.objects.filter(
            farm_id=farm_id,
            disease=disease
        ).order_by("-calculated_at").first()

        if not risk_score:
            return response.Response(
                {"error": "Risk score not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return response.Response({
            "farm_id": risk_score.farm_id,
            "disease": risk_score.disease,
            "score": risk_score.score,
            "band": risk_score.band,
            "window_start": risk_score.window_start,
            "window_end": risk_score.window_end,
            "calculated_at": risk_score.calculated_at,
        })