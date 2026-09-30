from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .services.planner import plan_trip


def _read_locations(request: HttpRequest) -> tuple[str, str]:
    start = finish = ""
    if request.method == "GET":
        start = (request.GET.get("start") or "").strip()
        finish = (request.GET.get("finish") or "").strip()
    else:
        content_type = request.content_type or ""
        if "application/json" in content_type:
            try:
                body = json.loads(request.body.decode("utf-8") or "{}")
            except json.JSONDecodeError as exc:
                raise ValueError("Request body must be valid JSON") from exc
            start = str(body.get("start") or "").strip()
            finish = str(body.get("finish") or "").strip()
        else:
            start = (request.POST.get("start") or "").strip()
            finish = (request.POST.get("finish") or "").strip()

    if not start or not finish:
        raise ValueError("Both 'start' and 'finish' locations are required")
    return start, finish


@csrf_exempt
@require_http_methods(["GET", "POST"])
def route_plan(request: HttpRequest) -> JsonResponse:
  
    try:
        start, finish = _read_locations(request)
        result = plan_trip(start, finish)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except Exception as exc:  
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse(result.to_dict())
