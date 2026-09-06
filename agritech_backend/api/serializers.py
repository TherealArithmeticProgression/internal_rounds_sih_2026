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
        read_only_fields = ("user",)


class SensorNodeSerializer(serializers.ModelSerializer):
    def validate_farm(self, farm):
        if farm.user != self.context["request"].user:
            raise serializers.ValidationError("You do not own this farm.")
        return farm
    class Meta:
        model = SensorNode
        fields = "__all__"


class SensorReadingSerializer(serializers.ModelSerializer):
    def validate_sensor_node(self, sensor_node):
        if sensor_node.farm.user != self.context["request"].user:
            raise serializers.ValidationError("You do not own this sensor node.")
        return sensor_node

    def validate(self, attrs):
        ranges = {"temperature": (-40, 70), "humidity": (0, 100), "soil_moisture": (0, 100), "rainfall_mm": (0, 500)}
        for field, (minimum, maximum) in ranges.items():
            value = attrs.get(field)
            if value is not None and not minimum <= value <= maximum:
                raise serializers.ValidationError({field: f"Must be between {minimum} and {maximum}."})
        return attrs
    class Meta:
        model = SensorReading
        fields = "__all__"


class TreatmentRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRecommendation
        fields = "__all__"


class DiseasePredictionSerializer(serializers.ModelSerializer):
    def validate_farm(self, farm):
        if farm.user != self.context["request"].user:
            raise serializers.ValidationError("You do not own this farm.")
        return farm
    class Meta:
        model = DiseasePrediction
        fields = "__all__"


class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = "__all__"

class PredictSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, allow_empty_file=False)
    farm_id = serializers.IntegerField(required=False, min_value=1)
    sensor_reading_id = serializers.IntegerField(required=False, min_value=1)
    captured_at = serializers.DateTimeField(required=False)

    def validate_image(self, image):
        if image.size > 8 * 1024 * 1024:
            raise serializers.ValidationError("Image must be 8 MB or smaller.")
        return image
