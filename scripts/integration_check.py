import os
import sys

import blogger
import images
import pipeline


REQUIRED_SETTINGS = (
    "GEMINI_API_KEY",
    "BLOGGER_BLOG_ID",
    "BLOGGER_CLIENT_ID",
    "BLOGGER_CLIENT_SECRET",
    "BLOGGER_REFRESH_TOKEN",
    "FACEBOOK_PAGE_ID",
    "FACEBOOK_PAGE_ACCESS_TOKEN",
    "CLOUDINARY_CLOUD_NAME",
    "CLOUDINARY_API_KEY",
    "CLOUDINARY_API_SECRET",
)


def _failure_detail(error):
    response = getattr(error, "resp", None)
    status = getattr(response, "status", None) or getattr(error, "http_code", None)
    return f"HTTP {status}" if status else type(error).__name__


def main():
    missing = [name for name in REQUIRED_SETTINGS if not os.getenv(name)]
    if missing:
        print("Missing required GitHub settings: " + ", ".join(missing))
        return 1

    checks = (
        ("Blogger OAuth", blogger.test_connection),
        ("Facebook Page read access", pipeline.verify_facebook_page),
        ("Cloudinary upload and cleanup", images.verify_cloudinary_upload_and_cleanup),
    )
    failures = 0
    for label, check in checks:
        try:
            check()
        except Exception as error:
            failures += 1
            print(f"{label}: failed ({_failure_detail(error)})")
        else:
            print(f"{label}: passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())