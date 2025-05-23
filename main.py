'''
Main script to fetch Substack posts and prepare for analysis.
'''
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List

from scraper import SubstackScraper, Post # Assuming scraper.py is in the same directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
SUBSTACK_URL = "https://jonathanpolitzki.substack.com/" # Your Substack URL
OUTPUT_DIR = "substack_data"
POSTS_FILE = os.path.join(OUTPUT_DIR, "substack_posts.json")
MAX_POSTS_TO_FETCH = 1000 # Adjust as needed

# --- Helper Functions ---
def ensure_dir(directory: str):
    """Ensures that the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def save_posts_to_json(posts: List[Post], filename: str):
    """Saves a list of Post objects to a JSON file."""
    ensure_dir(os.path.dirname(filename))
    # Convert datetime objects to ISO format strings for JSON serialization
    posts_data = []
    for post in posts:
        post_dict = post.__dict__
        if isinstance(post_dict['date'], datetime):
            post_dict['date'] = post_dict['date'].isoformat()
        posts_data.append(post_dict)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=4, ensure_ascii=False)
    logging.info(f"Successfully saved {len(posts)} posts to {filename}")

def load_posts_from_json(filename: str) -> List[Post]:
    """Loads posts from a JSON file."""
    if not os.path.exists(filename):
        logging.warning(f"Posts file not found: {filename}. Returning empty list.")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
    
    loaded_posts = []
    for data in posts_data:
        # Convert date string back to datetime object if it exists
        if data.get('date') and isinstance(data['date'], str):
            try:
                data['date'] = datetime.fromisoformat(data['date'])
            except ValueError:
                logging.warning(f"Could not parse date string: {data['date']} for post titled '{data.get('title')}'. Setting date to None.")
                data['date'] = None
        loaded_posts.append(Post(**data))
    logging.info(f"Successfully loaded {len(loaded_posts)} posts from {filename}")
    return loaded_posts

async def fetch_and_save_posts():
    """Fetches posts using the scraper and saves them."""
    logging.info(f"Starting Substack scrape for: {SUBSTACK_URL}")
    scraper = SubstackScraper(url=SUBSTACK_URL, max_posts=MAX_POSTS_TO_FETCH)
    posts = await scraper.scrape()

    if posts:
        save_posts_to_json(posts, POSTS_FILE)
    else:
        logging.warning("No posts were scraped.")
    return posts

# --- Placeholder for Gemini Analysis ---
def analyze_posts_with_gemini(posts: List[Post]):
    """
    Placeholder function for analyzing posts with Gemini long context.
    This function should:
    1. Prepare the data (e.g., concatenate content, format for Gemini API).
    2. Call the Gemini API with the prepared data.
    3. Process and log the analysis results.
    """
    if not posts:
        logging.warning("No posts available for analysis.")
        return

    logging.info(f"Starting analysis for {len(posts)} posts (placeholder)...")
    
    # Calculate total content size and token estimate
    total_chars = 0
    total_words = 0
    for post in posts:
        if post.content:
            total_chars += len(post.content)
            total_words += len(post.content.split())
        if post.title:
            total_chars += len(post.title)
            total_words += len(post.title.split())
    
    # Rough token estimation (1 token ≈ 4 characters or 0.75 words)
    estimated_tokens_by_chars = total_chars / 4
    estimated_tokens_by_words = total_words / 0.75
    estimated_tokens = int((estimated_tokens_by_chars + estimated_tokens_by_words) / 2)
    
    logging.info(f"Content statistics:")
    logging.info(f"  - Total characters: {total_chars:,}")
    logging.info(f"  - Total words: {total_words:,}")
    logging.info(f"  - Estimated tokens: {estimated_tokens:,}")
    
    # Example: Concatenate all content for a simple analysis
    # all_content = "\n\n---\n\n".join([f"Title: {p.title}\nDate: {p.date}\n\n{p.content}" for p in posts])
    
    # print("\n--- Combined Content for Gemini (First 1000 chars) ---")
    # print(all_content[:1000] + "...")
    # print("\n--- End of Combined Content Sample ---")

    # --- TODO: Implement Gemini API call here ---
    # 1. Authenticate with Gemini API
    # 2. Format the prompt and data for the API
    #    - Consider how to handle the total length of content if it exceeds context window.
    #    - You might need to send posts sentimientos, or summaries.
    # 3. Send the request to Gemini (e.g., using the `google-generativeai` library)
    #    Example prompt structure:
    #    prompt = f"""
    #    Analyze the following Substack posts by ITNAmatter.
    #    Identify the progression of themes and topics over time.
    #    What are the main arguments or ideas presented?
    #    Are there any recurring patterns or shifts in perspective?
    #    Provide a summary of the overall evolution of the blog's content.
    #    
    #    Posts data:
    #    {all_content}
    #    """
    # 4. Parse the response from Gemini
    # 5. Log or save the analysis results
    
    logging.info("Gemini analysis placeholder complete. Implement API calls to get actual analysis.")
    # For now, let's just print some basic stats
    if posts:
        logging.info(f"Total posts to analyze: {len(posts)}")
        
        # Get posts with valid dates
        posts_with_dates = [p for p in posts if p.date]
        if posts_with_dates:
            logging.info(f"Oldest post date: {min(p.date for p in posts_with_dates)}")
            logging.info(f"Newest post date: {max(p.date for p in posts_with_dates)}")
        else:
            logging.info("No posts have valid dates")

async def main():
    """Main execution function."""
    ensure_dir(OUTPUT_DIR)
    
    # Option 1: Always fetch new posts
    # posts = await fetch_and_save_posts()
    
    # Option 2: Load existing posts if available, otherwise fetch
    posts = load_posts_from_json(POSTS_FILE)
    if not posts:
        logging.info("No local posts found. Fetching from Substack...")
        posts = await fetch_and_save_posts()
    else:
        logging.info(f"Loaded {len(posts)} posts from {POSTS_FILE}. To refetch, delete this file.")

    if posts:
        analyze_posts_with_gemini(posts)
    else:
        logging.error("No posts available to analyze.")

if __name__ == "__main__":
    asyncio.run(main()) 