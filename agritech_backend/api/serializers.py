from rest_framework import serializers
from .models import (
    Farm,
    SensorNode,
    SensorReading,
    TreatmentRecommendation,
    DiseasePrediction,
    RiskScore,
)


class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = "__all__"


class SensorNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorNode
        fields = "__all__"


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = "__all__"


class TreatmentRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRecommendation
        fields = "__all__"


class DiseasePredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiseasePrediction
        fields = "__all__"


class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = "__all__"

class PredictSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True)