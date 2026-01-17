import os
import praw
import datetime
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "GeminiGemsExtractor/0.1")

def sanitize_filename(title):
    # Keep only alphanumeric and spaces, replace spaces with underscores, limit length
    clean = re.sub(r'[^a-zA-Z0-9 ]', '', title)
    return clean.replace(' ', '_')[:50]

def is_jan_2026(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.year == 2026 and dt.month == 1

def unescape_text(text):
    # Basic unescape if needed, PRAW usually handles well but just in case
    return text

def main():
    if not CLIENT_ID or not CLIENT_SECRET or "PLACEHOLDER" in CLIENT_ID:
        print("Error: Missing or placeholder Reddit API credentials in .env")
        print("Please update .env with your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return

    try:
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        
        # Verify read only mode
        print(f"Read only? {reddit.read_only}")

        subreddit = reddit.subreddit("GeminiAI")
        
        # Create output directory
        output_dir = "gems"
        os.makedirs(output_dir, exist_ok=True)

        print("Searching for Gems in r/GeminiAI (Jan 2026)...")
        
        # Searching strictly by timestamp is hard via search(), better to iterate new/hot if volume is low,
        # or use search with timestamp syntax (cloudsearch).
        # timestamp:1767225600..1769903999 (Jan 1 2026 to Jan 31 2026)
        # However, cloudsearch syntax on Reddit can be finicky.
        # Let's try iterating through submissions since it's a specific month.
        # Actually, for a specific past month, search is better.
        
        start_ts = int(datetime.datetime(2026, 1, 1).timestamp())
        end_ts = int(datetime.datetime(2026, 2, 1).timestamp())
        
        # We'll use a search query restricted to the subreddit
        # timestamp syntax: "timestamp:START..END"
        query = f"timestamp:{start_ts}..{end_ts}"
        
        count = 0
        
        # Note: PRAW search yields generator.
        # We can also just search for "Gem" or "Prompt" within that timeframe if we want to filter more.
        # But user asked to identify gems from *posts* in Jan 2026.
        # Let's try to fetch all posts if possible, but search with timestamp is most reliable for past windows.
        # Fallback: iterate 'new' and stop when date is too old? No, Jan 2026 is in the past (relative to 'now' in prompt? No, 'now' is Jan 2026 according to metadata).
        # Wait, metadata says current time is Jan 16, 2026. 
        # So we want "Jan 2026" which means "Month to Date" essentially.
        
        # Since we are IN Jan 2026, we can just iterate 'new' until we hit Dec 2025.
        
        for submission in subreddit.new(limit=None):
            sub_dt = datetime.datetime.fromtimestamp(submission.created_utc)
            
            if sub_dt.year < 2026:
                break # We went past Jan 2026
            
            if sub_dt.month == 1:
                # Check for "Gem" keywords
                content = (submission.title + " " + submission.selftext).lower()
                if any(k in content for k in ["gem", "prompt", "instruction", "system prompt", "shared gem"]):
                    print(f"Found potential Gem: {submission.title}")
                    
                    filename = f"{output_dir}/{sanitize_filename(submission.title)}.md"
                    
                    with open(filename, "w") as f:
                        f.write(f"# {submission.title}\n\n")
                        f.write(f"**Author**: u/{submission.author}\n")
                        f.write(f"**Date**: {sub_dt.strftime('%Y-%m-%d')}\n")
                        f.write(f"**URL**: {submission.url}\n\n")
                        f.write("## Description\n\n")
                        f.write(f"{submission.selftext}\n")
                    
                    count += 1

        print(f"Extraction complete. Found {count} gems.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
