import os
import json
import argparse
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/blogger"]

def get_service():
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["BLOGGER_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["BLOGGER_CLIENT_ID"],
        client_secret=os.environ["BLOGGER_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("blogger", "v3", credentials=credentials, cache_discovery=False)

def test_connection():
    service = get_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    blog = service.blogs().get(blogId=blog_id).execute(num_retries=2)
    created_at = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    post = service.posts().insert(
        blogId=blog_id,
        body={
            "title": f"PADMA BANGLA NEWS OAuth Test {created_at}",
            "content": "<p>Blogger OAuth draft connection test. This post is not published.</p>",
        },
        isDraft=True,
    ).execute(num_retries=2)
    if post.get("status", "DRAFT").upper() != "DRAFT":
        raise RuntimeError("Blogger test post was not returned as a draft")
    return {
        "status": "success",
        "blog_title": blog.get("name", ""),
        "draft_status": post.get("status", "DRAFT"),
        "draft_post_id": post.get("id", ""),
    }

def _find_existing_post(service, blog_id, source_id):
    marker = f"<!-- padma-news-source:{source_id} -->"
    page_token = None
    while True:
        response = service.posts().list(
            blogId=blog_id,
            status=["DRAFT", "LIVE"],
            maxResults=100,
            fetchBodies=True,
            pageToken=page_token,
        ).execute()
        for post in response.get("items", []):
            metadata = post.get("customMetaData", "")
            try:
                metadata = json.loads(metadata) if isinstance(metadata, str) else metadata
            except json.JSONDecodeError:
                metadata = {}
            if not isinstance(metadata, dict):
                metadata = {}
            if marker in post.get("content", "") or metadata.get("source_id") == source_id:
                return post
        page_token = response.get("nextPageToken")
        if not page_token:
            return None

def count_published_today():
    service = get_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    ist = ZoneInfo("Asia/Kolkata")
    today = datetime.now(ist).date()
    start = datetime.combine(today, time.min, tzinfo=ist).astimezone(timezone.utc)
    end = start + timedelta(days=1)
    page_token = None
    count = 0
    while True:
        response = service.posts().list(
            blogId=blog_id,
            status=["LIVE"],
            startDate=start.isoformat(),
            endDate=end.isoformat(),
            maxResults=100,
            pageToken=page_token,
        ).execute(num_retries=2)
        for post in response.get("items", []):
            published = post.get("published")
            if not published:
                continue
            published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
            if published_at.astimezone(ist).date() == today:
                count += 1
        page_token = response.get("nextPageToken")
        if not page_token:
            return count

def publish_post(title, content, *, labels=None, keywords=None, description="", permalink="", source_id="", is_draft=True):
    service = get_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    marker = f"<!-- padma-news-source:{source_id} -->" if source_id else ""
    body = {"title": title, "content": f"{marker}\n{content}"}
    if labels:
        body["labels"] = labels
    if description or source_id:
        body["customMetaData"] = json.dumps({
            "description": description,
            "keywords": keywords or labels or [],
            "permalink": permalink,
            "source_id": source_id,
        }, ensure_ascii=False)

    if marker:
        existing = _find_existing_post(service, blog_id, source_id)
        if existing:
            status = existing.get("status", "").upper()
            if status not in {"DRAFT", "LIVE"}:
                raise RuntimeError("Blogger returned an existing post with unknown status")
            if not is_draft and status == "DRAFT":
                post = service.posts().publish(
                    blogId=blog_id,
                    postId=existing["id"],
                ).execute()
            else:
                post = existing
            return {
                "id": post.get("id"),
                "url": post.get("url"),
                "title": post.get("title"),
                "published": post.get("published"),
                "status": post.get("status", status),
                "existing": True,
            }

    post = service.posts().insert(
        blogId=blog_id,
        body=body,
        isDraft=is_draft,
    ).execute()
    return {
        "id": post.get("id"),
        "url": post.get("url"),
        "title": post.get("title"),
        "published": post.get("published"),
        "status": post.get("status", ""),
        "existing": False,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", nargs="?")
    parser.add_argument("--test-draft", action="store_true", help="Verify OAuth and create a Blogger draft only")
    parser.add_argument("--publish", action="store_true", help="Publish live; otherwise save as a draft")
    args = parser.parse_args()
    import sys
    try:
        if args.test_draft:
            result = test_connection()
        else:
            if not args.title:
                parser.error("title is required unless --test-draft is set")
            content = sys.stdin.read()
            result = publish_post(args.title, content, is_draft=not args.publish)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        status = getattr(getattr(error, "resp", None), "status", None)
        detail = f"HTTP {status}" if status else type(error).__name__
        print(f"Blogger operation failed ({detail}); credential values were not logged.", file=sys.stderr)
        sys.exit(1)
