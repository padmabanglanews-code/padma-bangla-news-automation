import os
import json
import sys
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
    return build("blogger", "v3", credentials=credentials)

def publish_post(title, content):
    service = get_service()
    blog_id = os.environ["BLOGGER_BLOG_ID"]
    post = service.posts().insert(
        blogId=blog_id,
        body={"title": title, "content": content},
        isDraft=False,
    ).execute()
    return {"id": post.get("id"), "url": post.get("url"), "title": post.get("title")}

if __name__ == "__main__":
    title = sys.argv[1]
    content = sys.stdin.read()
    print(json.dumps(publish_post(title, content), ensure_ascii=False, indent=2))
