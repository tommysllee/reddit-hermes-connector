# Reddit Research Connector for Hermes

Read-only script that pulls public posts/comments from a fixed list of
subreddits and hands them to a locally-hosted Hermes AI agent for
summarization — used to spot recurring problems / market-demand
signals for market research.

**What this does NOT do:** post, comment, vote, message, or train/fine-tune
any model on Reddit data. It only reads public content and passes it to
Hermes for inference (summarization).

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # then fill in your real Reddit app credentials
export $(cat .env | xargs)  # or use a tool like python-dotenv
python reddit_connector.py
```

## Before running

Edit the `SUBREDDITS` list in `reddit_connector.py` to your actual
research targets.

## Getting Reddit credentials

1. Go to https://www.reddit.com/prefs/apps
2. Create a new app, type "script"
3. Copy the client ID (under the app name) and client secret
4. Put them in your `.env` file (never commit this)

## Pushing this to GitHub

```bash
cd reddit-hermes-connector
git init
git add reddit_connector.py requirements.txt .env.example README.md .gitignore
git commit -m "Initial reddit connector for Hermes research agent"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

Then paste the resulting GitHub URL into Reddit's Data Access Request form.
