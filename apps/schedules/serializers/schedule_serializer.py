# from rest_framework import serializers
# from apps.locations.models import Location


# class LocationSerializer(serializers.Serializer):
#     id = serializers.UUIDField()
#     name = serializers.CharField()
#     timezone = serializers.CharField()
#     address = serializers.CharField(
#         allow_blank=True, allow_null=True, required=False)


# class RequiredSkillSerializer(serializers.Serializer):
#     id = serializers.UUIDField()
#     name = serializers.CharField()


# class AssignmentUserSerializer(serializers.Serializer):
#     id = serializers.UUIDField()
#     username = serializers.CharField()
#     email = serializers.EmailField()
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()


# class ShiftAssignmentSerializer(serializers.Serializer):
#     id = serializers.UUIDField()
#     status = serializers.CharField()
#     user = AssignmentUserSerializer()


# class ShiftSerializer(serializers.Serializer):
#     id = serializers.UUIDField()
#     startTime = serializers.DateTimeField(source="start_time")
#     endTime = serializers.DateTimeField(source="end_time")
#     status = serializers.CharField()
#     isPremium = serializers.BooleanField(source="is_premium")
#     requiredHeadcount = serializers.IntegerField(source="required_headcount")
#     requiredSkill = RequiredSkillSerializer(source="required_skill")
#     assignments = ShiftAssignmentSerializer(many=True)


# class ScheduleSerializer(serializers.Serializer):
#     # here we list fields that are want to change to python dictionary, here we can define fields like model field
#     id = serializers.UUIDField()
#     week_start = serializers.DateTimeField()
#     status = serializers.CharField()
#     # you can add new field here,  not model field
#     remaining_cutoff = serializers.SerializerMethodField(
#         method_name="calcualte_cutoff")
#     publish_cutoff_hours = serializers.IntegerField()
#     location = LocationSerializer()
#     # location = serializers.PrimaryKeyRelatedField(
#     #     # queryset=Location.objects.all()
#     #     read_only=True
#     # )
#     # location = serializers.HyperlinkedRelatedField()

#     shifts = ShiftSerializer(many=True)

#     def calcualte_cutoff(sel, schedule):
#         return schedule.publish_cutoff_hours * 2.2


from rest_framework import serializers

from apps.locations.models import Location
from apps.schedules.models import Schedule, Shift, ShiftAssignment
from apps.users.models.skill import Skill
from apps.users.models.user import CustomUser


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "timezone", "address"]


class RequiredSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]


class AssignmentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "first_name", "last_name"]


class ShiftAssignmentSerializer(serializers.ModelSerializer):
    user = AssignmentUserSerializer(read_only=True)

    class Meta:
        model = ShiftAssignment
        fields = ["id", "status", "user"]


class ShiftSerializer(serializers.ModelSerializer):
    startTime = serializers.DateTimeField(source="start_time")
    endTime = serializers.DateTimeField(source="end_time")
    isPremium = serializers.BooleanField(source="is_premium")
    requiredHeadcount = serializers.IntegerField(source="required_headcount")
    requiredSkill = RequiredSkillSerializer(
        source="required_skill", read_only=True)
    assignments = ShiftAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Shift
        fields = [
            "id",
            "startTime",
            "endTime",
            "status",
            "isPremium",
            "requiredHeadcount",
            "requiredSkill",  # this field isnot available in the model so , it get it from the above ShiftSerializer
            "assignments",
        ]


class ScheduleReadSerializer(serializers.ModelSerializer):
    remaining_cutoff = serializers.SerializerMethodField()
    location = LocationSerializer(read_only=True)
    shifts = ShiftSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id",
            "week_start",
            "status",
            "remaining_cutoff",
            "publish_cutoff_hours",
            "location",
            "shifts",
        ]

    def get_remaining_cutoff(self, schedule):
        return schedule.publish_cutoff_hours * 2.2


class ScheduleCreateSerializer(serializers.ModelSerializer):
    weekStart = serializers.DateTimeField(source="week_start")
    # if we get locationId filed from the frontend the serialization looks like below
    # locationId = serializers.PrimaryKeyRelatedField(
    #     source="location",
    #     queryset=Location.objects.all()
    # )

    class Meta:
        model = Schedule
        fields = ["location", "weekStart", "publish_cutoff_hours"]

    # def validate(self, data):
    #     if data['password'] != data["confirm_password"]:
    #         return serializers.ValidationError('password do not match ')
    #     return data
    # def create(self, validated_data):
    #     # return super().create(validated_data)
    #     schedule = Schedule(**validated_data)
    #     schedule.other = 1
    #     schedule.save()
    #     return schedule

    # def update(self, instance, validated_data):
    #     # return super().update(instance, validated_data)
    #     instance.week_start = validated_data.get('week_start')
    #     instance.save()
    #     return instance


#    You can override the save method here
