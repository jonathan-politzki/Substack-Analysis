"""
Gemini-based analyzer for Substack posts.
"""
import os
# import json # No longer directly used here, moved to app.py or main.py
import logging
from typing import List, Dict, Any, Optional # Added Optional
from datetime import datetime
# import pandas as pd # Moved to app.py if only used for Streamlit app visualizations
# import matplotlib.pyplot as plt # Moved to app.py
# import matplotlib.dates as mdates # Moved to app.py

try:
    import google.generativeai as genai
except ImportError:
    genai = None
    logging.warning("google.generativeai not installed. Run: pip install google-generativeai")

from scraper import Post # Assuming scraper.py is in the same directory

logger = logging.getLogger(__name__)


class SubstackAnalyzer:
    def __init__(self, api_key: Optional[str] = None): # api_key can be None
        """Initialize the analyzer with Gemini API key."""
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            # This will be caught by the Streamlit app, no need to raise ValueError here for library use
            logger.warning("Gemini API key not provided. Analysis features will be disabled.")
            self.model = None
            return
        
        if genai:
            try:
                genai.configure(api_key=self.api_key)
                # Use Gemini 2.5 Pro Preview for the latest features
                self.model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
            except Exception as e:
                logger.error(f"Failed to configure Gemini or create model: {e}")
                self.model = None
        else:
            self.model = None
            
    def prepare_posts_for_analysis(self, posts: List[Post]) -> str:
        """Prepare posts as a formatted string for Gemini analysis."""
        posts_text = []
        
        # Sort posts by date (oldest first)
        sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)
        
        for post in sorted_posts:
            date_str = post.date.strftime("%Y-%m-%d") if post.date else "Unknown date"
            posts_text.append(f"""
--- POST ---
Title: {post.title}
Date: {date_str}
URL: {post.url}

Content:
{post.content}
--- END POST ---
""")
        
        return "\n\n".join(posts_text)
    
    def analyze_writing_evolution(self, posts: List[Post]) -> Dict[str, Any]:
        """Analyze the evolution of writing style and themes over time."""
        if not self.model:
            return {"error": "Gemini model not initialized or API key missing."}
            
        # Ensure posts are sorted for consistent analysis context
        sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)
        if not sorted_posts: # Handle empty list of posts
            return {"error": "No posts to analyze."}
            
        oldest_date_str = sorted_posts[0].date.strftime('%B %Y') if sorted_posts[0].date else 'Unknown'
        newest_date_str = sorted_posts[-1].date.strftime('%B %Y') if sorted_posts[-1].date else 'Unknown'
        
        posts_text = self.prepare_posts_for_analysis(sorted_posts)
        
        prompt = f"""You are analyzing a collection of Substack essays from the author ITNAmatter (Jonathan Politzki). 
These essays span from {oldest_date_str} to {newest_date_str}.

Please provide a comprehensive summary and analysis of these essays, covering:

1.  **Main Themes and Ideas**: What are the core subjects and concepts the author explores? How do they connect? Identify 3-5 dominant themes.
2.  **Author's Perspective/Voice**: Describe the author's general tone, style (e.g., analytical, reflective, narrative), and any distinct viewpoints or philosophical leanings.
3.  **Key Takeaways/Arguments**: What are 3-5 of the most significant insights or arguments presented across the essays? Briefly explain each.
4.  **Intellectual/Personal Journey**: Based on the progression of topics and style, what can you infer about the author's intellectual or personal development throughout this period of writing?
5.  **Potential Audience**: Who would most benefit or be interested in reading these essays?

Please synthesize this into a coherent narrative summary. Avoid just listing points; try to tell a story about the author's body of work as presented here.
Focus on the *content* and *ideas* more than just statistical patterns.

Here are the posts:

{posts_text}"""

        try:
            response = self.model.generate_content(prompt)
            return {
                "analysis": response.text,
                "total_posts": len(posts),
                "date_range": {
                    "start": min(p.date for p in posts if p.date).isoformat() if any(p.date for p in posts) else None,
                    "end": max(p.date for p in posts if p.date).isoformat() if any(p.date for p in posts) else None
                }
            }
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {e}")
            return {"error": str(e)}
    
    def analyze_specific_themes(self, posts: List[Post], themes: List[str]) -> Dict[str, Any]:
        """Analyze specific themes across all posts."""
        if not self.model:
            return {"error": "Gemini model not initialized or API key missing."}
            
        posts_text = self.prepare_posts_for_analysis(posts)
        themes_str = ", ".join(themes)
        
        prompt = f"""Analyze how the following themes appear and evolve across these Substack posts by ITNAmatter (Jonathan Politzki):
Themes to analyze: {themes_str}

For each theme:
1. Which posts discuss this theme most prominently? (List titles and dates)
2. How does the author's perspective or depth of discussion on this theme evolve (if at all) across the posts?
3. What are some unique insights or key arguments the author provides related to this theme?
4. Rate the theme's importance/centrality in this collection of essays (1-10, where 10 is very central).

Provide a structured response, addressing each theme separately.

Posts:
{posts_text}"""

        try:
            response = self.model.generate_content(prompt)
            return {
                "themes_analysis": response.text,
                "themes_analyzed": themes
            }
        except Exception as e:
            logger.error(f"Error during theme analysis: {e}")
            return {"error": str(e)}
    
    # Visualization and detailed statistics parts are removed as they will be handled by app.py or main.py
    # to keep this module focused on Gemini interaction and post preparation.
    # def generate_statistics(self, posts: List[Post]) -> Dict[str, Any]: ...
    # def create_visualizations(self, posts: List[Post], output_dir: str = "substack_data"): ...

# Removed stray </rewritten_file> tag 