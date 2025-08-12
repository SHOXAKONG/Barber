from rest_framework import serializers
from src.apps.user.models import Roles

class UpdateRoleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    default_from_hour = serializers.TimeField(required=False)
    default_to_hour = serializers.TimeField(required=False)

    def validate(self, data):
        role_id = data.get('role_id')

        role = Roles.objects.only("id").filter(id=role_id).first()
        if not role:
            raise serializers.ValidationError({"role_id": "Invalid role id"})
        if role.name == 'Client':
            raise serializers.ValidationError({"role_id": "You selected Client id, but it will be added authomatically!"})

        from_hour = data.get('default_from_hour')
        to_hour = data.get('default_to_hour')

        if from_hour and to_hour:
            if from_hour >= to_hour:
                raise serializers.ValidationError({
                    "default_to_hour": "End time must be later than start time."
                })

        data['role'] = role
        return data