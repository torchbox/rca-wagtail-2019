from rest_framework import serializers

from rca.programmes.models import DegreeLevel


class DegreeLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeLevel
        fields = ("id", "title")
