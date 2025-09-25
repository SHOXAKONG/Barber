from rest_framework import serializers


class WeeklyClientsSerializer(serializers.Serializer):
    weekday = serializers.IntegerField()
    clients = serializers.IntegerField()