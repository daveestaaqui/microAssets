import os
import praw
import time

def main():
    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
        user_agent="CSSGradientBot 1.0",
        username=os.environ.get("REDDIT_USERNAME", "YOUR_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD", "YOUR_PASSWORD")
    )
    
    subreddits = ["webdev", "css", "frontend", "webdesign"]
    keywords = ["gradient", "css background", "generator", "color scheme"]
    
    print(f"Tracking subreddits: {', '.join(subreddits)}")
    subreddit = reddit.subreddit('+'.join(subreddits))
    
    # Watch for new mentions
    for submission in subreddit.stream.submissions(skip_existing=True):
        title = submission.title.lower()
        text = submission.selftext.lower()
        
        for k in keywords:
            if k in title or k in text:
                print(f"[FOUND] {submission.title}")
                print(f"URL: {submission.url}")
                # Log opportunity for manual interaction
                with open("reddit_opportunities.log", "a") as log:
                    log.write(f"Match: {k}\nTitle: {submission.title}\nURL: {submission.url}\n\n")
                break

if __name__ == '__main__':
    print("Marketing Bot: CSS Gradient Outreach initiated...")
    main()
