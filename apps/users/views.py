from zoneinfo import ZoneInfo
from datetime import timedelta
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.shortcuts import render
from .models import CustomUser, Skill
import json
from apps.locations.models import Location
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from datetime import datetime
from django.utils.dateparse import parse_datetime

# Create your views here.


# @csrf_exempt
def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('data', data)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            phone_number = data.get('phone_number')
            role = data.get('role')
            if not username or not email or not password:
                return JsonResponse({'error': 'missing fields'}, status=400)
            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                role=role
            )
            return JsonResponse({'message': 'user created successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# @csrf_exempt
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("see the login data", data)
            email = data.get('email')
            password = data.get('password')
            if not email or not password:
                return JsonResponse({'error': 'Missing credentials'}, status=400)
              # authenticate user
            user = authenticate(request, username=email, password=password)
            print("see the logged in user userDetail", user)
            print(user.id)
            print(user.email)
            print(user.username)
            if user is None:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
            login(request, user)

            data = {"user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
            }}
            return JsonResponse(data)
            # return JsonResponse({'message': "Logged in successfully"}, status=200)

            # if not user:
            #     return JsonResponse({'error': "AN authorized"}, status=403)
            # else:
            #     return JsonResponse({'message': "logged in successfully"}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({"message": "CSRF cookie set"})


def get_user_skill(request: HttpRequest) -> HttpResponse:
    skills = Skill.objects.all()
    data = [
        {
            "id": str(s.id),
            "name": s.name
        }
        for s in skills
    ]
    return JsonResponse(data, safe=False)


def get_available_staff(request: HttpRequest) -> JsonResponse:
    location_id = request.GET.get("locationId")
    skill_id = request.GET.get("skillId")
    shift_start = request.GET.get("shiftStart")
    shift_end = request.GET.get("shiftEnd")

    # print("see all id", location_id, skill_id, shift_start, shift_end)

    # Convert string → datetime
    shift_start = parse_datetime(shift_start)
    shift_end = parse_datetime(shift_end)

    # STEP 1: DB filtering (same as Prisma where)
    staff = CustomUser.objects.filter(
        is_active=True,
        role="STAFF",
        locations__id=location_id,
        skills__id=skill_id,
    ).prefetch_related(
        "shift_assignments__shift",   # adjust to your related_name
        "recurring_availabilities",
        "availability_exceptions",
    ).distinct()
    # print("see the staff", staff)
    for staff1 in staff:
        print(staff1)

    try:
        location = Location.objects.get(id=location_id)
    except Location.DoesNotExist:
        return JsonResponse({"data": []})

    valid_staff = []

    # STEP 2: Business logic filtering
    for user in staff:
        assignments = user.shift_assignments.all()

        # 1. Overlap check
        has_conflict = any(
            has_overlap(a.shift, shift_start, shift_end)
            for a in assignments
        )
        print("Is hasConflict", has_conflict)
        if has_conflict:
            continue

        # 2. Rest rule check
        violates_rest_rule = any(
            violates_rest(a.shift, shift_start)
            for a in assignments
        )
        print("violatesRest", violates_rest_rule)
        if violates_rest_rule:
            continue

        # 3. Availability check
        available = is_available(
            user,
            shift_start,
            shift_end,
            location.timezone
        )
        print("available", available)
        if not available:
            continue

        valid_staff.append({
            "id": str(user.id),
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
        })

    # STEP 3: Return result
    return JsonResponse(valid_staff, safe=False)


def has_overlap(existing_shift, new_start, new_end):
    """
    existing_shift: Shift object
    new_start, new_end: datetime
    """
    return (
        existing_shift.start_time < new_end and
        existing_shift.end_time > new_start
    )


REST_HOURS = 10


def violates_rest(existing_shift, new_start):
    """
    existing_shift: Shift object
    new_start: datetime
    """
    rest_period = timedelta(hours=REST_HOURS)

    # If new shift starts too soon after existing shift ends
    if new_start < existing_shift.end_time + rest_period:
        return True

    return False


def is_available(user, shift_start: datetime, shift_end: datetime, timezone: str):
    """
    user: CustomUser
    shift_start, shift_end: datetime (can be UTC or naive)
    timezone: string (e.g. "Africa/Addis_Ababa")
    """

    tz = ZoneInfo(timezone)

    # 1. Convert shift → LOCATION TIMEZONE
    shift_start = shift_start.astimezone(tz)
    shift_end = shift_end.astimezone(tz)

    shift_date = shift_start.date()
    shift_day = shift_start.isoweekday()  # 0 = Monday
    print("see the shift_date", shift_date)
    print("see the shift_day", shift_day)
    shift_start_min = shift_start.hour * 60 + shift_start.minute
    shift_end_min = shift_end.hour * 60 + shift_end.minute

    # Helper (same as JS)
    def normalize_range(start, end):
        return (start, end + 1440) if end <= start else (start, end)

    norm_shift_start, norm_shift_end = normalize_range(
        shift_start_min, shift_end_min
    )
    print("see the norm_shift_start", norm_shift_start)
    print("see the norm_shift_end", norm_shift_end)
    # ---------------------------------------
    # 2. CHECK EXCEPTIONS (HIGHEST PRIORITY)
    # ---------------------------------------
    exceptions = user.availability_exceptions.filter(date=shift_date)
    print("see the exceptions ", exceptions)
    for ex in exceptions:
        # Full-day exception
        if ex.is_full_day or not ex.start_time or not ex.end_time:
            return ex.is_available

        # Convert HH:mm → minutes
        ex_start = ex.start_time.hour * 60 + ex.start_time.minute
        ex_end = ex.end_time.hour * 60 + ex.end_time.minute

        norm_ex_start, norm_ex_end = normalize_range(ex_start, ex_end)

        # Overlap check (same as JS)
        overlaps = (
            norm_shift_start < norm_ex_end
            and norm_shift_end > norm_ex_start
        )

        if overlaps:
            return ex.is_available  # override

    # ---------------------------------------
    # 3. CHECK RECURRING AVAILABILITY
    # ---------------------------------------
    recurring = user.recurring_availabilities.all()
    # print("see the recurring", recurring)
    for r in recurring:
        print("see the recurring one by one", r)
        print("see the resurring day", r.day_of_week)
        if r.day_of_week != shift_day:
            continue

        avail_start = r.start_time.hour * 60 + r.start_time.minute
        avail_end = r.end_time.hour * 60 + r.end_time.minute
        print("see the avail_start ", avail_start)
        print("see the avail_end ", avail_end)

        norm_avail_start, norm_avail_end = normalize_range(
            avail_start, avail_end
        )

        # Must fully fit inside availability
        if (
            norm_shift_start >= norm_avail_start
            and norm_shift_end <= norm_avail_end
        ):
            return True

    return False
