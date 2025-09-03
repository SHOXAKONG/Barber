from rest_framework import serializers

class BarberActivitySerializer(serializers.Serializer):
    barber_id = serializers.IntegerField()
    barber_name = serializers.CharField()
    monthly_clients = serializers.IntegerField()
    weekly_clients = serializers.IntegerField()
