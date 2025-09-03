from rest_framework import serializers

class ServiceUsageSerializer(serializers.Serializer):
    service__id = serializers.IntegerField()
    service__name = serializers.CharField()
    usage_count = serializers.IntegerField()
