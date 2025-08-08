from rest_framework import serializers
from src.apps.breakes.models import Break


class BreakSerializers(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields = ['id', 'start_time', 'end_time', 'reason']


class BreakCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Break
        fields = '__all__'

    def create(self, validated_data):
        barber = validated_data.pop('barber', None)
        instance = Break.objects.create(**validated_data)
        if barber:
            instance.barber = barber
            instance.save()
        return instance

