from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
# import uuid
from django.contrib.auth import get_user_model
from .models import Schedule, ScheduleStatus, Shift, ShiftStatus
from apps.locations.models import Location
from apps.users.models.skill import Skill
# from django.db.models import F
from django.db.models import Prefetch
from django.db import transaction
from apps.schedules.models import ShiftAssignment, AssignmentStatus


# @csrf_exempt


def create_schedule(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        # print("User Object:", request.user)
        # print("User ID:", request.user.id)
        # print("User Email:", request.user.email)

        data = json.loads(request.body)
        print("see the shift detail", data)
        # print("schedule data", data)
        location_id = data.get("locationId")
        week_start = data.get("weekStart")
        publish_cutoff_hours = data.get("publish_cutoff_hours", 48)

        # Validate required fields
        if not location_id or not week_start:
            return JsonResponse(
                {"error": "location_id and week_start are required"},
                status=400
            )

        # Get location
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return JsonResponse({"error": "Location not found"}, status=404)

        # Parse datetime
        week_start_dt = parse_datetime(week_start)
        if not week_start_dt:
            return JsonResponse({"error": "Invalid week_start format"}, status=400)

        # Create schedule
        schedule = Schedule.objects.create(
            location=location,
            creator=request.user,
            week_start=week_start_dt,
            status=ScheduleStatus.DRAFT,
            publish_cutoff_hours=publish_cutoff_hours
        )

        return JsonResponse({
            "message": "Schedule created successfully",
            "schedule": {
                "id": str(schedule.id),
                "location": str(schedule.location_id),
                "week_start": schedule.week_start,
                "status": schedule.status,
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# def get_schedule(request: HttpRequest) -> HttpResponse:
#     # Use .filter() to limit results to a specific creator
#     # We use request.user.id to get the ID of the currently logged-in user
#     schedules = Schedule.objects.filter(creator_id=request.user.id)

#     data = list(schedules.values(
#         'status',
#         'publish_cutoff_hours',
#         scheduleId=F('id'),
#         weekStart=F('week_start'),
#         locationName=F('location__name'),
#         locationId=F('location__id'),
#         createdBy=F('creator__email')
#     ))
#     print("see the schedule data", data)
#     return JsonResponse(data, safe=False)


def get_schedule(request: HttpRequest) -> HttpResponse:
    # 1. Fetch objects (use select_related to make the join efficient)
    # schedules = Schedule.objects.filter(
    #     creator_id=request.user.id).select_related('location', 'creator')

    schedules = (
        Schedule.objects
        .filter(creator_id=request.user.id)
        .select_related("location", "creator")
        .prefetch_related(
            Prefetch(
                "shifts",
                queryset=Shift.objects.select_related("required_skill").prefetch_related(
                    "assignments__user"
                )
            )
        )
    )
    # 2. Manually build the nested structure
    # data = [
    #     {
    #         "status": s.status,
    #         "publish_cutoff_hours": s.publish_cutoff_hours,
    #         "scheduleId": s.id,
    #         "weekStart": s.week_start,
    #         "createdBy": s.creator.email,
    #         "location": {
    #             "id": s.location.id,
    #             "name": s.location.name,
    #             "timeZone": s.location.timezone
    #         }
    #     }
    #     for s in schedules
    # ]

    # return JsonResponse(data, safe=False)
    data = []

    for s in schedules:
        schedule_data = {
            "status": s.status,
            "publish_cutoff_hours": s.publish_cutoff_hours,
            "scheduleId": s.id,
            "weekStart": s.week_start,
            "createdBy": s.creator.email,
            "location": {
                "id": s.location.id,
                "name": s.location.name,
                "timeZone": s.location.timezone
            },
            "shifts": []
        }

        for shift in s.shifts.all():
            shift_data = {
                "shiftId": shift.id,
                "startTime": shift.start_time,
                "endTime": shift.end_time,
                "status": shift.status,
                "isPremium": shift.is_premium,
                "requiredHeadcount": shift.required_headcount,
                "requiredSkill": {
                    "id": shift.required_skill.id,
                    "name": shift.required_skill.name,
                },
                "assignments": []
            }

            for assignment in shift.assignments.all():
                shift_data["assignments"].append({
                    "assignmentId": assignment.id,
                    "status": assignment.status,
                    "user": {
                        "id": assignment.user.id,
                        "email": assignment.user.email,
                        "firstName": assignment.user.first_name,
                        "lastName": assignment.user.last_name,

                    }
                })

            schedule_data["shifts"].append(shift_data)

        data.append(schedule_data)

    return JsonResponse(data, safe=False)


def create_shift(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        data = json.loads(request.body)
        print("see the create_shift detail", data)
        schedule_id = data.get("scheduleId")
        start_time = data.get("startTime")
        assignedUserIds = data.get("assignedUserIds")
        end_time = data.get("endTime")
        required_skill_id = data.get("requiredSkillId")
        required_headcount = data.get("requiredHeadcount", 1)
        is_premium = data.get("is_premium", False)

        # -------------------------
        # Validate required fields
        # -------------------------
        if not all([schedule_id, start_time, end_time, required_skill_id]):
            return JsonResponse(
                {"error": "schedule_id, start_time, end_time, required_skill_id are required"},
                status=400
            )

        # -------------------------
        # Get schedule
        # -------------------------
        schedule = Schedule.objects.filter(id=schedule_id).first()
        if not schedule:
            return JsonResponse({"error": "Schedule not found"}, status=404)

        # -------------------------
        # Get location from schedule (IMPORTANT: avoid redundancy)
        # -------------------------
        location = schedule.location

        # -------------------------
        # Get skill
        # -------------------------
        skill = Skill.objects.filter(id=required_skill_id).first()
        if not skill:
            return JsonResponse({"error": "Skill not found"}, status=404)

        # -------------------------
        # Parse datetime
        # -------------------------
        start_dt = parse_datetime(start_time)
        end_dt = parse_datetime(end_time)

        if not start_dt or not end_dt:
            return JsonResponse({"error": "Invalid datetime format"}, status=400)

        if start_dt >= end_dt:
            return JsonResponse(
                {"error": "start_time must be before end_time"},
                status=400
            )

        # -------------------------
        # Create shift
        # -------------------------
        # shift = Shift.objects.create(
        #     schedule=schedule,
        #     location=location,
        #     start_time=start_dt,
        #     end_time=end_dt,
        #     required_skill=skill,
        #     required_headcount=required_headcount,
        #     creator=request.user,
        #     status=ShiftStatus.DRAFT,
        #     is_premium=is_premium
        # )
        try:
            CustomUser = get_user_model()
            with transaction.atomic():
                shift = Shift.objects.create(
                    schedule=schedule,
                    location=location,
                    start_time=start_dt,
                    end_time=end_dt,
                    required_skill=skill,
                    required_headcount=required_headcount,
                    creator=request.user,
                    status=ShiftStatus.DRAFT,
                    is_premium=is_premium
                )

    # Create assignments (if any)
                if assignedUserIds:
                    users = CustomUser.objects.filter(id__in=assignedUserIds)

                    if users.count() != len(set(assignedUserIds)):
                        raise ValueError(
                            "One or more assigned users not found")

                    ShiftAssignment.objects.bulk_create([
                        ShiftAssignment(
                            shift=shift,
                            user=user,
                            status=AssignmentStatus.ASSIGNED
                        )
                        for user in users
                    ])

            return JsonResponse({
                "message": "Shift created successfully",
                "shift": {
                    "id": str(shift.id),
                    "schedule_id": str(shift.schedule_id),
                    "location_id": str(shift.location_id),
                    "start_time": shift.start_time,
                    "end_time": shift.end_time,
                    "status": shift.status,
                    "is_premium": shift.is_premium
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({"faild to create shift and shift Assignment": str(e)}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_shifts(request: HttpRequest) -> HttpResponse:
    data = ShiftAssignment.objects.filter(
        user_id=request.user.id,
        status__in=["ASSIGNED", "PENDING_SWAP"]
    ).select_related(
        "shift",
        "shift__location",
        "shift__required_skill",
    ).prefetch_related(
        "shift__swap_requests",
        "shift__swap_requests__requester",
        "shift__swap_requests__target_user",
    )

    result = [
        {
            "id": sa.id,
            "status": sa.status,
            "shift": {
                "id": sa.shift.id,
                "startTime": sa.shift.start_time,
                "endTime": sa.shift.end_time,

                "location": {
                    "id": sa.shift.location.id,
                    "name": sa.shift.location.name,
                },

                "requiredSkill": {
                    "id": sa.shift.required_skill.id,
                    "name": sa.shift.required_skill.name,
                },

                "swapRequests": [
                    {
                        "id": sr.id,
                        "requester": {
                            "id": sr.requester.id,
                            "name": sr.requester.username,
                        },
                        "targetUser": {
                            "id": sr.target_user.id,
                            "name": sr.target_user.username,
                        },
                    }
                    for sr in sa.shift.swap_requests.all()
                ],
            },
        }
        for sa in data
    ]
    return JsonResponse(result, safe=False)
