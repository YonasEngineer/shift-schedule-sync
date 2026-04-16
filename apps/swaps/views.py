import json
from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import SwapRequest, SwapRequestType
from apps.schedules.models import Shift
from django.contrib.auth import get_user_model

User = get_user_model()


@require_POST
def create_swap(request: HttpRequest) -> JsonResponse:
    try:
        body = json.loads(request.body)
        print("see the swap requested data", body)
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
            status="PENDING"
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
