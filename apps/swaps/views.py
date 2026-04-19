from .models import SwapRequest, SwapManagerStatus
from apps.schedules.models import ShiftAssignment, AssignmentStatus
# from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpRequest, Http404
from .models import SwapRequest
from django.http import JsonResponse
import json
import uuid
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from .models import SwapRequest, SwapRequestType, SwapRequestStatus
from apps.schedules.models import Shift
from django.contrib.auth import get_user_model
from django.views import View
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
User = get_user_model()


@require_POST
def create_swap(request: HttpRequest) -> JsonResponse:
    try:
        body = json.loads(request.body)
        shift_id = body.get("shiftId")
        swap_type = body.get("type")
        target_user_id = body.get("targetUserId")

        # --- Basic validation ---
        if not shift_id or not swap_type:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if swap_type not in SwapRequestType.values:
            return JsonResponse({"error": "Invalid swap type"}, status=400)

        # --- Get objects ---
        try:
            shift = Shift.objects.get(id=shift_id)
        except Shift.DoesNotExist:
            return JsonResponse({"error": "Shift not found"}, status=404)

        target_user = None
        if target_user_id:
            try:
                target_user = User.objects.get(id=target_user_id)
            except User.DoesNotExist:
                return JsonResponse({"error": "Target user not found"}, status=404)

        # --- Business logic (important) ---
        # prevent swapping with yourself
        if target_user and target_user == request.user:
            return JsonResponse({"error": "Cannot swap with yourself"}, status=400)

        # optional: prevent duplicate active requests
        exists = SwapRequest.objects.filter(
            shift=shift,
            requester=request.user,
            status=SwapRequestStatus.PENDING
        ).exists()

        if exists:
            return JsonResponse({"error": "You already have a pending request for this shift"}, status=400)

        # --- Create swap ---
        swap = SwapRequest.objects.create(
            shift=shift,
            requester=request.user,
            target_user=target_user,
            type=swap_type,
            expires_at=timezone.now() + timezone.timedelta(hours=24)  # optional expiry
        )

        return JsonResponse({
            "message": "Swap request created successfully",
            "swapId": str(swap.id)
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class GetSwaps(View):
    def get(self, request):
        swaps = SwapRequest.objects.filter(
            Q(target_user=request.user) |
            Q(requester=request.user)
        ).select_related(
            "shift", "requester", "target_user"
        ).order_by("-created_at")

        data = [
            {
                "id": str(swap.id),
                "status": swap.status,
                "type": swap.type,
                "createdAt": swap.created_at,
                "managerStatus": swap.manager_status,
                # shift
                "shift": {
                    "id": str(swap.shift.id),
                    "startTime": swap.shift.start_time,
                    "endTime": swap.shift.end_time,
                } if swap.shift else None,

                # requester
                "requester": {
                    "id": str(swap.requester.id),
                    "name": swap.requester.username,
                    "firstName": swap.requester.first_name,
                    "secondName": swap.requester.last_name,
                } if swap.requester else None,

                # target user
                "targetUser": {
                    "id": str(swap.target_user.id),
                    "name": swap.target_user.username,
                    "firstName": swap.target_user.first_name,
                    "secondName": swap.target_user.last_name,
                } if swap.target_user else None,
            }
            for swap in swaps
        ]

        return JsonResponse(data, safe=False)


def get_needing_manager_approval(request: HttpRequest, location_id: uuid.UUID) -> JsonResponse:

    swaps = SwapRequest.objects.filter(
        status=SwapRequestStatus.ACCEPTED,
        processed_at__isnull=True,
        shift__location_id=location_id
    ).select_related(
        "shift", "requester", "target_user"
    ).order_by("-created_at")

    data = [
        {
            "id": str(swap.id),
            "status": swap.status,
            "type": swap.type,
            "createdAt": swap.created_at,

            "shift": {
                "id": str(swap.shift.id),
                "startTime": swap.shift.start_time,
                "endTime": swap.shift.end_time,
            } if swap.shift else None,

            "requester": {
                "id": str(swap.requester.id),
                "name": swap.requester.username,
                "firstName": swap.requester.first_name,
                "secondName": swap.requester.last_name,
            } if swap.requester else None,

            "targetUser": {
                "id": str(swap.target_user.id),
                "name": swap.target_user.username,
                "firstName": swap.target_user.first_name,
                "secondName": swap.target_user.last_name,
            } if swap.target_user else None,
        }
        for swap in swaps
    ]

    return JsonResponse(data, safe=False)


@require_http_methods(["PATCH"])
def accept_swap(request: HttpRequest, swap_id: str) -> HttpResponse:
    try:
        # 1. Fetch swap with related shift
        swap = SwapRequest.objects.select_related("shift").get(id=swap_id)

        # Validation: swap exists
        if not swap:
            return JsonResponse({"error": "Swap request not found"}, status=404)

        # Validation: status must be PENDING
        if swap.status != "PENDING":
            return JsonResponse(
                {"error": "Swap is no longer pending"}, status=400
            )

        target_user = request.user

        # Validation: check target user
        if swap.target_user and swap.target_user.id != target_user.id:
            return JsonResponse(
                {"error": "You are not the designated target for this swap"},
                status=400,
            )

        # 2. Transaction block
        with transaction.atomic():

            # A. Update swap status
            swap.status = "ACCEPTED"
            # swap.processed_at = timezone.now()  # optional
            swap.save()

            # --- OPTIONAL LOGIC (same as your JS comments) ---

            # # B. Create new assignment (if needed)
            # ShiftAssignment.objects.create(
            #     shift=swap.shift,
            #     user=target_user,
            # )

            # # C. Cancel other pending swaps for same shift/requester
            # SwapRequest.objects.filter(
            #     shift=swap.shift,
            #     requester=swap.requester,
            #     status="PENDING"
            # ).exclude(id=swap.id).update(status="CANCELLED")

        return JsonResponse(
            {
                "message": "Swap accepted successfully",
                "swap_id": swap.id,
                "status": swap.status,
            },
            status=200,
        )

    except ObjectDoesNotExist:
        return JsonResponse({"error": "Swap request not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
def reject_swap(request: HttpRequest, swap_id) -> HttpResponse:
    with transaction.atomic():
        try:
            swap = SwapRequest.objects.select_for_update().get(id=swap_id)
        except SwapRequest.DoesNotExist:
            raise Http404("Swap not found")

        # revert assignment back
        ShiftAssignment.objects.filter(
            shift_id=swap.shift_id,
            user_id=swap.requester_id
        ).update(status="ASSIGNED")

        # update swap status
        swap.status = "REJECTED"
        swap.save()

        return JsonResponse({
            "id": str(swap.id),
            "status": swap.status
        })


def manager_approve(request: HttpRequest) -> HttpResponse:
    swap_id = request.GET.get("swapId")

    # request.POST.get("swapId")
    manager_id = request.user.id  # assuming authenticated user is manager

    if not swap_id:
        return JsonResponse({"error": "swapId is required"}, status=400)

    try:
        with transaction.atomic():

            # 1. Fetch swap
            swap = SwapRequest.objects.select_related(
                "shift", "requester", "target_user"
            ).filter(id=swap_id).first()
            if not swap or not swap.target_user:
                return JsonResponse({"error": "Swap not found or no target user"}, status=404)

            # 2. Update old assignment (requester → COMPLETED_SWAP)
            ShiftAssignment.objects.filter(
                shift=swap.shift,
                user=swap.requester
            ).update(status=AssignmentStatus.COMPLETED_SWAP)

            # 3. Create new assignment (target user → ASSIGNED)
            ShiftAssignment.objects.update_or_create(
                shift=swap.shift,
                user=swap.target_user,
                defaults={"status": "ASSIGNED"}
            )

            # 4. Approve swap
            swap.manager_status = SwapManagerStatus.APPROVED
            swap.processed_at = timezone.now()
            swap.processed_by_id = manager_id
            swap.save(update_fields=["manager_status",
                      "processed_at", "processed_by"])

            return JsonResponse({
                "id": str(swap.id),
                "manager_status": swap.manager_status
            })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_POST
def manager_reject(request: HttpRequest) -> HttpResponse:
    # print("we are here>>>>>>>>>>>>>>>>>>")
    manager_id = request.user.id  # assuming logged-in manager
    data = json.loads(request.body)

    swap_id = data.get("swapId")
    if not swap_id:
        return JsonResponse({"error": "swapId is required"}, status=400)

    with transaction.atomic():
        try:
            swap = SwapRequest.objects.select_for_update().get(id=swap_id)
        except SwapRequest.DoesNotExist:
            raise Http404("Swap not found")

        # revert assignment back
        ShiftAssignment.objects.filter(
            shift_id=swap.shift_id,
            user_id=swap.requester_id
        ).update(status="ASSIGNED")

        # update swap with manager decision
        swap.processed_by_id = manager_id
        swap.processed_at = timezone.now()
        swap.manager_status = "REJECTED"
        swap.save()

        return JsonResponse({
            "id": str(swap.id),
            "manager_status": swap.manager_status,
            "processed_by": manager_id,
            "processed_at": swap.processed_at.isoformat()
        })
