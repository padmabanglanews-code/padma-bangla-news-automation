import sys

from pipeline import verify_facebook_page


def main():
    try:
        verify_facebook_page()
    except Exception:
        print("Facebook Page verification failed. Check the configured Page ID, token, and permissions.")
        return 1

    print("Facebook Page verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
