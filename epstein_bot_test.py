#this is epstein_bot.py with certain parts commented out. i used this file to make sure epstein_bot.py was working

import praw
import logging
import time
from reddit_api_key import key
# IMPORTANT: Replace with your actual Reddit API credentials
# REDDIT_CLIENT_ID = 'YOUR_CLIENT_ID'
# REDDIT_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
# REDDIT_USER_AGENT = 'KeywordCommentBot by /u/YOUR_REDDIT_USERNAME' # Replace with your Reddit username
# REDDIT_USERNAME = 'YOUR_REDDIT_USERNAME'
# REDDIT_PASSWORD = 'YOUR_REDDIT_PASSWORD'

# Subreddit to monitor. Use 'all' for r/all, or a specific subreddit like 'test'
# HIGHLY RECOMMENDED: Start with a private subreddit like 'test' or your own
# private subreddit for testing to avoid unintended comments on public subreddits.
SUBREDDIT_TO_MONITOR = 'all'

# Timeframe for top posts (e.g., 'hour', 'day', 'week', 'month', 'year', 'all')
TOP_POST_TIMEFRAME = 'hour'

# Number of top posts to fetch
POST_LIMIT = 100
# The list of words to look for in post titles (case-insensitive)
WORD_LIST = ["test", "example", "hello", "bot", "python", "script"] # Expand this list as needed!

# The comment text to post if a keyword is found
COMMENT_TEXT = "your comment here"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_reddit_instance():
    """Initializes and returns a PRAW Reddit instance."""
    logging.info("Initializing Reddit instance...")
    try:
        from reddit_utils import reddit 
        reddit.read_only = False # Set to False to allow commenting
        logging.info(f"Authenticated as {reddit.user.me()} (read_only={reddit.read_only})")
        return reddit
    except Exception as e:
        logging.error(f"Failed to initialize Reddit instance: {e}")
        logging.error("Please ensure your Reddit API credentials are correct and you have internet access.")
        return None

def run_bot():
    """Main function to run the Reddit keyword comment bot."""
    reddit = get_reddit_instance()
    if not reddit:
        logging.error("Bot cannot run without a valid Reddit instance.")
        return

    subreddit = reddit.subreddit(SUBREDDIT_TO_MONITOR)
    logging.info(f"Fetching {POST_LIMIT} top posts from r/{SUBREDDIT_TO_MONITOR} ({TOP_POST_TIMEFRAME})...")

    # Keep track of comments already processed to avoid duplicate comments on rerun
    # In a real bot, you might use a database for this. For simplicity, we'll use a set in memory.
    processed_submissions = set()

    try:
        # Fetch top posts based on the specified timeframe and limit
        for submission in subreddit.top(time_filter=TOP_POST_TIMEFRAME, limit=POST_LIMIT):
            # Skip if the post is sticky or already processed
            if submission.stickied or submission.id in processed_submissions:
                continue

            logging.info(f"\nProcessing post: '{submission.title}' (ID: {submission.id})")

            # Convert title to lowercase for case-insensitive comparison
            title_words = submission.title.lower().split()

            found_keyword = False
            for keyword in WORD_LIST:
                if keyword.lower() in title_words: # Check if the keyword exists in the title's words
                    logging.info(f"  Found keyword '{keyword}' in title.")
                    found_keyword = True
                    break # Found a keyword, no need to check others for this title

            # if found_keyword:
                # Check if the bot has already commented on this post
                # This is a basic check. For more robust checks, you'd iterate submission.comments
                # and check if comment.author.name == REDDIT_USERNAME.
                # For simplicity here, we'll assume we only comment once per run.
                # try:
                #     # Post the comment
                #     comment = submission.reply(COMMENT_TEXT)
                #     logging.info(f"  Successfully posted comment (ID: {comment.id}) to post {submission.id}.")
                #     processed_submissions.add(submission.id) # Mark as processed
                #     time.sleep(10) # Pause to respect Reddit API rate limits
                # except praw.exceptions.RedditAPIException as e:
                #     logging.warning(f"  Could not comment on post {submission.id} (Error: {e}). Skipping.")
                #     # Common errors: COMMENT_TOO_FAST, BANNED_FROM_SUBREDDIT, etc.
                # except Exception as e:
                #     logging.error(f"  An unexpected error occurred while commenting on post {submission.id}: {e}")
            # else:
            #     logging.info("  No keywords found in title.")

        # logging.info("\nFinished processing top posts for this run.")

    except Exception as e:
        logging.error(f"An error occurred during bot execution: {e}")
        logging.error("Please check your internet connection, Reddit API credentials, and subreddit name.")

if __name__ == "__main__":
    logging.info("Starting Reddit Keyword Comment Bot...")
    run_bot()

print




import logging

logging.info("Hello, world!")
