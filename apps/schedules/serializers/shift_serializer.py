from rest_framework import serializers
from apps.schedules.models import Shift, ShiftAssignment
from apps.users.models.skill import Skill
from apps.users.models.user import CustomUser
from apps.locations.models import Location
from apps.swaps.models import SwapRequest


# class ShiftSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Shift
#         fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "name"]


class SwapRequestSerializer(serializers.ModelSerializer):
    requester = UserSimpleSerializer()
    target_user = UserSimpleSerializer()

    class Meta:
        model = SwapRequest
        fields = ["id", "requester", "target_user"]


class ShiftSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    required_skill = SkillSerializer()
    swap_requests = SwapRequestSerializer(many=True)

    class Meta:
        model = Shift
        fields = [
            "id",
            "startTime",
            "endTime",
            "location",
            "requiredSkill",
            "swapRequests",
        ]


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer()
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ShiftAssignment
        fields = ["id", "status", "shift"]
