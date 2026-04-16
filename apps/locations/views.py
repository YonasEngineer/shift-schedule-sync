from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import UserLocation
from django.db.models import F
# Create your views here.


from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpRequest
from .models import UserLocation


def get_manager_location(request: HttpRequest, user_id: str):
    # 1. Fix: Use the string 'location' (the model field name)
    # Also, we filter by the user_id passed from the URL

    # Below is used to  Fetches UserLocation + Location in ONE query (JOIN) ✅
    # user_location = get_object_or_404(
    #     UserLocation.objects.select_related("location"),
    #     user_id=user_id,
    #     role='MANAGER'
    # ).location

    # Fetches UserLocation first, then Location in SECOND query ❌
    # user_location = get_object_or_404(
    #     UserLocation,
    #     user_id=user_id,
    #     role='MANAGER'
    # ).location

    locations_queryset = UserLocation.objects.filter(
        user_id=user_id).select_related('location')
    # print("locations_queryset", locations_queryset)
    # print("list", list(locations_queryset))
    # 2. Fetch the specific manager record
    user_location = get_object_or_404(
        UserLocation, user_id=user_id, role='MANAGER').location
    # print('see the user_location', user_location)
    # print("Manager Record:", user_location)

    # 3. Convert the queryset to a list of dictionaries
    # Note: 'location__name' works because 'location' is the ForeignKey name
    data = list(locations_queryset.values(
        'role',
        isCertified=F('is_certified'),
        # This renames 'location__name' to 'location_name'
        locationName=F('location__name'),
        # This renames 'location__id' to 'location_id'
        locationId=F('location__id'),
        timezone=F('location__timezone')
    ))

    return JsonResponse({"locations": data}, safe=False)
