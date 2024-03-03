from rest_framework import serializers
from .models import *


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class OutputMultiModelSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course__name = serializers.CharField()
    course__maxlisteners = serializers.IntegerField()
    course__startat = serializers.DateTimeField()
    course__minlisteners = serializers.IntegerField()


class StudyingPlanSerializer(serializers.Serializer):
    course__name = serializers.CharField()
    lesson__name = serializers.CharField()
