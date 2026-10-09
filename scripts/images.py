import os
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlsplit


CLOUDINARY_SETTINGS = (
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
)
APPROVED_IMAGE_DOMAINS = ("abplive.com", "abpnews.com")


class ImageIntegrationError(RuntimeError):
    pass


def missing_cloudinary_settings():
    return [name for name in CLOUDINARY_SETTINGS if not os.getenv(name)]


def is_approved_news_image_url(url):
    try:
        parsed = urlsplit(url or "")
        host = (parsed.hostname or "").lower().rstrip(".")
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and any(host == domain or host.endswith("." + domain) for domain in APPROVED_IMAGE_DOMAINS)
    )


def _cloudinary_client():
    missing = missing_cloudinary_settings()
    if missing:
        raise ImageIntegrationError("Missing GitHub settings: " + ", ".join(missing))
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.utils
    except ImportError:
        raise ImageIntegrationError("Cloudinary SDK is not installed") from None

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True,
    )
    return cloudinary.uploader, cloudinary.utils


def _branded_fallback_path():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise ImageIntegrationError("Pillow is not installed") from None

    temporary = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    temporary.close()
    path = Path(temporary.name)
    image = Image.new("RGB", (1200, 675), (10, 48, 55))
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 0), (860, 0), (480, 675), (0, 675)], fill=(17, 91, 91))
    draw.polygon([(790, 0), (1200, 0), (1200, 675), (410, 675)], fill=(22, 66, 77))
    draw.rectangle((72, 72, 82, 312), fill=(231, 173, 73))
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 58)
    except OSError:
        font = ImageFont.load_default(size=48)
    draw.text((112, 92), "PADMA", font=font, fill=(255, 255, 255))
    draw.text((112, 170), "BANGLA NEWS", font=font, fill=(255, 255, 255))
    draw.line((112, 278, 505, 278), fill=(231, 173, 73), width=5)
    image.save(path, format="PNG", optimize=True)
    return path


def _cloudinary_url(utils, public_id):
    url, _ = utils.cloudinary_url(
        public_id,
        secure=True,
        transformation=[
            {"width": 1200, "height": 675, "crop": "limit"},
            {"quality": "auto", "fetch_format": "auto"},
        ],
    )
    if not url.startswith("https://res.cloudinary.com/"):
        raise ImageIntegrationError("Cloudinary did not return a secure hosted image URL")
    return url


def upload_news_image(source_url, source_id, headline=""):
    uploader, utils = _cloudinary_client()
    public_id = f"news-{source_id}"
    upload_source = source_url if is_approved_news_image_url(source_url) else None
    fallback_path = None
    try:
        if upload_source:
            try:
                response = uploader.upload(
                    upload_source,
                    folder="padma-bangla-news/news",
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                )
            except Exception as error:
                if getattr(error, "http_code", None) in {401, 403}:
                    raise ImageIntegrationError(
                        f"Cloudinary rejected its credentials (HTTP {error.http_code})"
                    ) from None
                upload_source = None

        if not upload_source:
            fallback_path = _branded_fallback_path()
            response = uploader.upload(
                str(fallback_path),
                folder="padma-bangla-news/news",
                public_id=public_id,
                overwrite=True,
                resource_type="image",
            )
        hosted_id = response.get("public_id")
        if not hosted_id:
            raise ImageIntegrationError("Cloudinary upload returned no image identifier")
        return _cloudinary_url(utils, hosted_id)
    except ImageIntegrationError:
        raise
    except Exception as error:
        status = getattr(error, "http_code", None)
        detail = f"HTTP {status}" if status else type(error).__name__
        raise ImageIntegrationError(f"Cloudinary image upload failed ({detail})") from None
    finally:
        if fallback_path:
            fallback_path.unlink(missing_ok=True)


def verify_cloudinary_upload_and_cleanup():
    uploader, _ = _cloudinary_client()
    fallback_path = _branded_fallback_path()
    public_id = f"integration-{uuid.uuid4().hex}"
    uploaded_id = None
    try:
        response = uploader.upload(
            str(fallback_path),
            folder="padma-bangla-news/integration-tests",
            public_id=public_id,
            overwrite=False,
            resource_type="image",
        )
        uploaded_id = response.get("public_id")
        secure_url = response.get("secure_url", "")
        if not uploaded_id or not secure_url.startswith("https://res.cloudinary.com/"):
            if uploaded_id:
                try:
                    uploader.destroy(uploaded_id, invalidate=True, resource_type="image")
                except Exception:
                    pass
            raise ImageIntegrationError("Cloudinary smoke upload returned an invalid response")
    except ImageIntegrationError:
        raise
    except Exception as error:
        status = getattr(error, "http_code", None)
        detail = f"HTTP {status}" if status else type(error).__name__
        raise ImageIntegrationError(f"Cloudinary smoke upload failed ({detail})") from None
    finally:
        fallback_path.unlink(missing_ok=True)

    try:
        deletion = uploader.destroy(uploaded_id, invalidate=True, resource_type="image")
    except Exception as error:
        raise ImageIntegrationError(
            f"Cloudinary smoke asset uploaded but cleanup failed ({type(error).__name__})"
        ) from None
    if deletion.get("result") != "ok":
        raise ImageIntegrationError("Cloudinary smoke asset could not be removed")
    return {"status": "success", "uploaded_and_removed": True}