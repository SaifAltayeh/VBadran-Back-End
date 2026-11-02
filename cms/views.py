import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .defaults import DEFAULT_HOME
from .models import SiteHome


def deep_merge(base, incoming):
    if not isinstance(base, dict) or not isinstance(incoming, dict):
        return incoming
    merged = dict(base)
    for key, value in incoming.items():
        merged[key] = deep_merge(base.get(key), value) if key in base else value
    return merged


def normalize_home(data):
    home = deep_merge(DEFAULT_HOME, data or {})
    hero = home.get("hero") or {}
    title = hero.get("title") or {}
    for lang in ("en", "ar"):
        value = title.get(lang)
        if isinstance(value, list):
            title[lang] = " ".join(str(part).strip() for part in value if str(part).strip())
    hero["title"] = title
    home["hero"] = hero
    return home


class SiteHomeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(normalize_home(SiteHome.load().data or {}))


class SiteHomeAdminView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(normalize_home(SiteHome.load().data or {}))

    def patch(self, request):
        page = SiteHome.load()
        payload = request.data.get("data", request.data)
        page.data = normalize_home(deep_merge(page.data or {}, payload))
        page.save(update_fields=["data"])
        return Response(page.data)


class MediaUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Choose an image file."}, status=400)
        content_type = getattr(upload, "content_type", "") or ""
        if not content_type.startswith("image/"):
            return Response({"detail": "Only image uploads are allowed."}, status=400)
        if upload.size and upload.size > 8 * 1024 * 1024:
            return Response({"detail": "Images must be 8MB or smaller."}, status=400)

        extension = Path(upload.name or "upload.jpg").suffix.lower() or ".jpg"
        if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            extension = ".jpg"
        filename = f"cms/{uuid.uuid4().hex}{extension}"
        saved = default_storage.save(filename, upload)
        relative = f"{settings.MEDIA_URL.rstrip('/')}/{saved.lstrip('/')}"
        return Response(
            {
                "url": request.build_absolute_uri(relative),
                "path": relative,
            }
        )
