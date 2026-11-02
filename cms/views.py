import base64
import io
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError
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


def image_to_data_url(upload, max_side=1200, quality=72):
    try:
        image = Image.open(upload)
        image.load()
    except UnidentifiedImageError as exc:
        raise ValueError("Only image uploads are allowed.") from exc

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGBA")
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


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
        if upload.size and upload.size > 8 * 1024 * 1024:
            return Response({"detail": "Images must be 8MB or smaller."}, status=400)

        try:
            data_url = image_to_data_url(upload)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        # Keep a file copy for debugging/local previews when the filesystem is writable.
        try:
            upload.seek(0)
            extension = Path(upload.name or "upload.jpg").suffix.lower() or ".jpg"
            if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
                extension = ".jpg"
            filename = f"cms/{uuid.uuid4().hex}{extension}"
            saved = default_storage.save(filename, upload)
            relative = f"{settings.MEDIA_URL.rstrip('/')}/{saved.lstrip('/')}"
            absolute = request.build_absolute_uri(relative)
        except Exception:
            relative = ""
            absolute = data_url

        return Response(
            {
                "url": data_url,
                "path": data_url,
                "file_url": absolute,
                "file_path": relative,
            }
        )


class VideoUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        upload = request.FILES.get("file")
        if not upload:
            return Response({"detail": "Choose a video file."}, status=400)

        content_type = (upload.content_type or "").lower()
        extension = Path(upload.name or "upload.mp4").suffix.lower() or ".mp4"
        allowed = {".mp4", ".webm", ".mov", ".m4v"}
        if extension not in allowed and not content_type.startswith("video/"):
            return Response({"detail": "Upload an MP4 or WebM video."}, status=400)

        max_bytes = int(3.5 * 1024 * 1024)
        if upload.size and upload.size > max_bytes:
            return Response(
                {"detail": "Videos must be 3.5MB or smaller. Use a short 1280×720 MP4."},
                status=400,
            )

        payload = upload.read()
        mime = content_type if content_type.startswith("video/") else "video/mp4"
        if extension == ".webm":
            mime = "video/webm"
        elif extension == ".mov":
            mime = "video/quicktime"
        encoded = base64.b64encode(payload).decode("ascii")
        data_url = f"data:{mime};base64,{encoded}"
        return Response({"url": data_url, "path": data_url})
