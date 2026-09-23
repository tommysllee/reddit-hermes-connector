"""
Reddit Research Connector for Hermes AI Agent
----------------------------------------------
Read-only script that pulls public posts + top comments from a
configured list of subreddits, and hands the raw text over to a
locally-hosted Hermes agent for summarization / pain-point analysis.

Scope, by design:
  - Read-only. Uses Reddit's app-only OAuth2 grant (no user login,
    no write scopes). Cannot post, comment, vote, or message.
  - Only fetches subreddits explicitly listed below.
  - Sends fetched text to Hermes purely for inference/summarization.
    Nothing here trains or fine-tunes a model on Reddit data.
"""

import os
import json
import time
import requests
import praw

# ---- Config -----------------------------------------------------------

# Edit this list to match your actual research targets before running.
SUBREDDITS = [
    "personalfinance",
    "financialplanning",
    "Indonesia",
    "IndonesiaBusiness",
    "smallbusiness",
    "entrepreneur",
]

POSTS_PER_SUBREDDIT = 15          # posts pulled per subreddit, per run
COMMENTS_PER_POST = 10            # top-level comments kept per post
HERMES_ENDPOINT = os.environ.get("HERMES_ENDPOINT", "http://localhost:8008/ingest")

# Create a "script" type app at https://www.reddit.com/prefs/apps
# Never commit real credentials — set these as environment variables.
REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
REDDIT_USER_AGENT = os.environ.get(
    "REDDIT_USER_AGENT", "hermes-research-connector/1.0 by u/garethorus"
)

# ---- Reddit client: read-only, no login, no write scopes --------------

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)
reddit.read_only = True


def fetch_subreddit(name: str) -> list[dict]:
    """Pull recent hot posts + top comments from one subreddit."""
    items = []
    subreddit = reddit.subreddit(name)

    for post in subreddit.hot(limit=POSTS_PER_SUBREDDIT):
        post.comments.replace_more(limit=0)
        top_comments = [c.body for c in post.comments[:COMMENTS_PER_POST]]
        items.append({
            "subreddit": name,
            "post_id": post.id,
            "title": post.title,
            "body": post.selftext,
            "score": post.score,
            "url": f"https://reddit.com{post.permalink}",
            "top_comments": top_comments,
        })
    return items


def send_to_hermes(batch: list[dict]) -> None:
    """Hand the raw text off to the local Hermes agent for analysis."""
    try:
        resp = requests.post(HERMES_ENDPOINT, json={"items": batch}, timeout=30)
        resp.raise_for_status()
        print(f"Sent {len(batch)} items to Hermes ({resp.status_code}).")
    except requests.RequestException as e:
        print(f"Could not reach Hermes at {HERMES_ENDPOINT}: {e}")
        fname = f"reddit_batch_{int(time.time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
        print(f"Saved batch locally to {fname} instead.")


def main():
    all_items = []
    for sr in SUBREDDITS:
        print(f"Fetching r/{sr} ...")
        all_items.extend(fetch_subreddit(sr))
        time.sleep(2)  # stay well under rate limits, don't hammer the API

    send_to_hermes(all_items)


if __name__ == "__main__":
    main()
