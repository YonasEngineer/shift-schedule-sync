from rest_framework import serializers
from apps.schedules.models import Shift, ShiftAssignment
from apps.users.models.skill import Skill
from apps.users.models.user import CustomUser
from apps.locations.models import Location
from apps.swaps.models import SwapRequest


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
        fields = ["id", "username"]


class SwapRequestSerializer(serializers.ModelSerializer):
    requester = UserSimpleSerializer()
    # target_user = UserSimpleSerializer()
    targetUser = UserSimpleSerializer(source="target_user")

    class Meta:
        model = SwapRequest
        fields = ["id", "requester", "targetUser"]


class ShiftSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    # required_skill = SkillSerializer()
    # swap_requests = SwapRequestSerializer(many=True)

    swapRequests = SwapRequestSerializer(source="swap_requests", many=True)
    requiredSkill = SkillSerializer(source="required_skill")
    startTime = serializers.DateTimeField(source="start_time")
    endTime = serializers.DateTimeField(source="end_time")

    class Meta:
        model = Shift
        fields = [
            "id",
            "startTime",
            "endTime",
            "location",
            "swapRequests",
            "requiredSkill",
        ]


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    shift = ShiftSerializer()
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = ShiftAssignment
        fields = ["id", "status", "shift"]
