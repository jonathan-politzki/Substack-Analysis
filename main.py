'''
Main script to fetch Substack posts and analyze them with Gemini.
'''
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List

from scraper import SubstackScraper, Post
from analyzer import SubstackAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
SUBSTACK_URL = "https://jonathanpolitzki.substack.com/"
OUTPUT_DIR = "substack_data"
POSTS_FILE = os.path.join(OUTPUT_DIR, "substack_posts.json")
ANALYSIS_FILE = os.path.join(OUTPUT_DIR, "analysis_results.json")
MAX_POSTS_TO_FETCH = 1000

# --- Helper Functions ---
def ensure_dir(directory: str):
    """Ensures that the specified directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def save_posts_to_json(posts: List[Post], filename: str):
    """Saves a list of Post objects to a JSON file."""
    posts_data = []
    for post in posts:
        posts_data.append({
            "title": post.title,
            "url": post.url,
            "content": post.content,
            "date": post.date.isoformat() if post.date else None,
            "subtitle": post.subtitle,
        })
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Successfully saved {len(posts)} posts to {filename}")

def load_posts_from_json(filename: str) -> List[Post]:
    """Loads posts from a JSON file."""
    if not os.path.exists(filename):
        logging.warning(f"Posts file not found: {filename}. Returning empty list.")
        return []
    
    with open(filename, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
    
    posts = []
    for data in posts_data:
        post = Post(
            title=data['title'],
            url=data['url'],
            content=data['content'],
            date=datetime.fromisoformat(data['date']) if data['date'] else None,
            subtitle=data.get('subtitle', ''),
        )
        posts.append(post)
    
    logging.info(f"Loaded {len(posts)} posts from {filename}")
    return posts

def save_analysis_results(results: dict, filename: str):
    """Save analysis results to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logging.info(f"Analysis results saved to {filename}")

# --- Main Functions ---
async def fetch_posts(url: str, max_posts: int) -> List[Post]:
    """Fetches posts from the given Substack URL."""
    scraper = SubstackScraper(url, max_posts)
    posts = await scraper.scrape()
    return posts

def analyze_posts_with_gemini(posts: List[Post]):
    """
    Analyze posts using Gemini API.
    """
    if not posts:
        logging.warning("No posts available for analysis.")
        return
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logging.error("GEMINI_API_KEY not found in environment variables.")
        logging.info("To use Gemini analysis:")
        logging.info("1. Get an API key from https://makersuite.google.com/app/apikey")
        logging.info("2. Set it as an environment variable: export GEMINI_API_KEY='your-key-here'")
        logging.info("3. Or create a .env file with: GEMINI_API_KEY=your-key-here")
        return
    
    try:
        analyzer = SubstackAnalyzer(api_key)
        
        logging.info("Generating statistics...")
        stats = analyzer.generate_statistics(posts)
        
        logging.info("Creating visualizations...")
        viz_path = analyzer.create_visualizations(posts, OUTPUT_DIR)
        
        logging.info("Running Gemini analysis on writing evolution...")
        evolution_analysis = analyzer.analyze_writing_evolution(posts)
        
        # Analyze specific themes
        themes = ["technology", "AI", "entrepreneurship", "personal growth", "philosophy", "startup"]
        logging.info(f"Analyzing themes: {themes}")
        themes_analysis = analyzer.analyze_specific_themes(posts, themes)
        
        # Combine all results
        results = {
            "statistics": stats,
            "visualization_path": viz_path,
            "evolution_analysis": evolution_analysis,
            "themes_analysis": themes_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Save results
        save_analysis_results(results, ANALYSIS_FILE)
        
        # Print summary
        print("\n" + "="*50)
        print("ANALYSIS COMPLETE")
        print("="*50)
        print(f"Total posts analyzed: {stats['total_posts']}")
        print(f"Total words: {stats['total_words']:,}")
        print(f"Average words per post: {stats['average_words_per_post']:,}")
        print(f"Date range: {posts[0].date.strftime('%B %Y')} to {posts[-1].date.strftime('%B %Y')}")
        print(f"\nVisualization saved to: {viz_path}")
        print(f"Full analysis saved to: {ANALYSIS_FILE}")
        
        if 'analysis' in evolution_analysis:
            print("\n" + "="*50)
            print("WRITING EVOLUTION SUMMARY (from Gemini)")
            print("="*50)
            print(evolution_analysis['analysis'][:1000] + "...")  # First 1000 chars
            
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        logging.info("Make sure you have installed all dependencies: pip install -r requirements.txt")

async def main():
    """Main function to coordinate scraping and analysis."""
    ensure_dir(OUTPUT_DIR)
    
    # Try to load existing posts first
    posts = load_posts_from_json(POSTS_FILE)
    
    if not posts:
        logging.info("No local posts found. Fetching from Substack...")
        logging.info(f"Starting Substack scrape for: {SUBSTACK_URL}")
        posts = await fetch_posts(SUBSTACK_URL, MAX_POSTS_TO_FETCH)
        
        if posts:
            save_posts_to_json(posts, POSTS_FILE)
        else:
            logging.error("Failed to fetch posts from Substack.")
            return
    
    # Analyze posts
    analyze_posts_with_gemini(posts)
    
    # Log summary
    if posts:
        logging.info(f"Total posts to analyze: {len(posts)}")
        
        # Get date range
        dates = [p.date for p in posts if p.date]
        if dates:
            logging.info(f"Oldest post date: {min(dates)}")
            logging.info(f"Newest post date: {max(dates)}")

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    asyncio.run(main()) 