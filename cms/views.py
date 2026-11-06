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
from .sanitize import replace_stale_copy


def clean_socials(socials):
    items = []
    for item in socials or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        href = str(item.get("href") or "").strip()
        if label or href:
            items.append({"label": label, "href": href})
    return items


def deep_merge(base, incoming):
    if not isinstance(base, dict) or not isinstance(incoming, dict):
        return incoming
    merged = dict(base)
    for key, value in incoming.items():
        merged[key] = deep_merge(base.get(key), value) if key in base else value
    return merged


def normalize_home(data):
    home = replace_stale_copy(deep_merge(DEFAULT_HOME, data or {}))
    hero = home.get("hero") or {}
    title = hero.get("title") or {}
    for lang in ("en", "ar"):
        value = title.get(lang)
        if isinstance(value, list):
            title[lang] = " ".join(str(part).strip() for part in value if str(part).strip())
    hero["title"] = title
    home["hero"] = hero
    site = home.get("site") or {}
    default_site = DEFAULT_HOME.get("site") or {}
    hrefs = " ".join(str((item or {}).get("href", "")) for item in (site.get("socials") or []) if isinstance(item, dict))
    stale = (
        site.get("email") == "hello@vbadran.com"
        or "962790000000" in str(site.get("phoneHref") or "")
        or ("instagram.com/vbadran/" in hrefs and "instagram.com/vbadrann" not in hrefs)
        or "wa.me/962" in hrefs
    )
    if stale:
        site["email"] = default_site.get("email", site.get("email"))
        site["phoneDisplay"] = default_site.get("phoneDisplay", site.get("phoneDisplay"))
        site["phoneHref"] = default_site.get("phoneHref", site.get("phoneHref"))
        site["socials"] = list(default_site.get("socials") or [])
    else:
        site["socials"] = clean_socials(site.get("socials"))
    home["site"] = site
    hero = home.get("hero") or {}
    primary = hero.get("primary") or {}
    secondary = hero.get("secondary") or {}
    if primary.get("href") == "/pricing":
        primary["href"] = "/programs"
        hero["primary"] = primary
    if secondary.get("href") == "/pricing":
        secondary["href"] = "/programs"
        hero["secondary"] = secondary
    home["hero"] = hero
    sections = home.get("sections") or {}
    cta = sections.get("cta") or {}
    if cta.get("href") == "/pricing":
        cta["href"] = "/programs"
        sections["cta"] = cta
    pricing = sections.get("pricing") or {}
    pricing["visible"] = False
    sections["pricing"] = pricing
    home["sections"] = sections
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

        if getattr(settings, "ON_VERCEL", False) or not settings.DEBUG:
            return Response(
                {
                    "detail": "File upload is not available on this host. Paste a YouTube, Vimeo, or direct MP4 URL. Base64 data URLs are not production video storage.",
                },
                status=400,
            )

        max_bytes = int(12 * 1024 * 1024)
        if upload.size and upload.size > max_bytes:
            return Response(
                {
                    "detail": "Videos must be 12MB or smaller. For staging and production, paste a YouTube or Vimeo URL instead of uploading a file.",
                },
                status=400,
            )

        filename = f"videos/{uuid.uuid4().hex}{extension}"
        saved = default_storage.save(filename, upload)
        relative = f"{settings.MEDIA_URL.rstrip('/')}/{saved.lstrip('/')}"
        absolute = request.build_absolute_uri(relative)
        return Response(
            {
                "url": relative,
                "path": relative,
                "file_url": absolute,
                "storage": "local-media",
                "warning": "Saved to local media. Hosted YouTube, Vimeo, or MP4 URLs are required on staging and production. Base64 data URLs are not video storage.",
            }
        )
