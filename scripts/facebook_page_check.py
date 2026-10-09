import sys

from pipeline import PipelineError, verify_facebook_page


def main():
    try:
        verify_facebook_page()
    except PipelineError as error:
        print(f"Facebook Page verification failed: {error}")
        return 1
    except Exception as error:
        print(
            f"Facebook Page verification failed ({type(error).__name__}). "
            "Check secure configuration and try again."
        )
        return 1

    print("Facebook Page verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
