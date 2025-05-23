"""
Streamlit web application for Substack essay analysis with Gemini.
"""
import streamlit as st
import os
import asyncio
from typing import List, Optional
from datetime import datetime

from scraper import SubstackScraper, Post # Assuming scraper.py is in the same directory
from analyzer import SubstackAnalyzer   # Assuming analyzer.py is in the same directory

# --- Configuration & State Management ---
if 'posts' not in st.session_state:
    st.session_state.posts: Optional[List[Post]] = None
if 'analysis_summary' not in st.session_state:
    st.session_state.analysis_summary: Optional[str] = None
if 'qa_answer' not in st.session_state:
    st.session_state.qa_answer: Optional[str] = None
if 'gemini_api_key_valid' not in st.session_state:
    st.session_state.gemini_api_key_valid: bool = False

# --- Helper Functions (from main.py, adapted for Streamlit) ---
def get_analyzer_instance(api_key: str) -> Optional[SubstackAnalyzer]:
    try:
        analyzer = SubstackAnalyzer(api_key)
        st.session_state.gemini_api_key_valid = True
        return analyzer
    except ValueError as e:
        st.error(f"Error initializing Analyzer (likely API key issue): {e}")
        st.session_state.gemini_api_key_valid = False
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during Analyzer initialization: {e}")
        st.session_state.gemini_api_key_valid = False
        return None

async def fetch_posts_async(url: str, max_posts: int = 1000) -> List[Post]:
    """Fetches posts from the given Substack URL."""
    scraper = SubstackScraper(url, max_posts)
    loop = asyncio.get_event_loop()
    posts = await loop.run_in_executor(None, lambda: asyncio.run(scraper.scrape()))
    return posts

# --- Gemini Interaction Functions ---
def get_corpus_text(posts: List[Post]) -> str:
    """Combines all post content into a single string for Gemini Q&A."""
    if not posts:
        return ""
    # Sort posts by date (oldest first) for consistent context
    sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)
    
    corpus_parts = []
    for i, post in enumerate(sorted_posts):
        date_str = post.date.strftime("%Y-%m-%d") if post.date else "Unknown date"
        corpus_parts.append(f"--- ESSAY {i+1} ---\nTitle: {post.title}\nDate: {date_str}\n\n{post.content}\n--- END ESSAY {i+1} ---\n")
    return "\n".join(corpus_parts)

def ask_gemini_about_corpus(analyzer: SubstackAnalyzer, posts: List[Post], question: str) -> str:
    if not analyzer or not analyzer.model:
        return "Error: Gemini Analyzer not initialized. Please check your API key."
    if not posts:
        return "No posts loaded to ask questions about."
    if not question.strip():
        return "Please enter a question."

    corpus = get_corpus_text(posts)
    
    # Get date range for context
    oldest_post_date = min(p.date for p in posts if p.date) if any(p.date for p in posts) else None
    newest_post_date = max(p.date for p in posts if p.date) if any(p.date for p in posts) else None
    date_range_str = ""
    if oldest_post_date and newest_post_date:
        date_range_str = f"The essays span from {oldest_post_date.strftime('%B %Y')} to {newest_post_date.strftime('%B %Y')}."

    prompt = f"""You are a helpful AI assistant answering questions about a collection of Substack essays written by ITNAmatter (Jonathan Politzki).
{date_range_str}

Here is the full text of the essays:
{corpus}

Based *only* on the provided essays, please answer the following question:
Question: {question}

Answer:"""

    try:
        response = analyzer.model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error querying Gemini: {e}")
        return f"Error querying Gemini: {e}"

def generate_overall_summary(analyzer: SubstackAnalyzer, posts: List[Post]) -> str:
    if not analyzer or not analyzer.model:
        return "Error: Gemini Analyzer not initialized."
    if not posts:
        return "No posts to summarize."

    # Re-use the writing evolution analysis prompt for a good overall summary
    # Ensure posts are sorted for consistent analysis context
    sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)
    oldest_date_str = sorted_posts[0].date.strftime('%B %Y') if sorted_posts and sorted_posts[0].date else 'Unknown'
    newest_date_str = sorted_posts[-1].date.strftime('%B %Y') if sorted_posts and sorted_posts[-1].date else 'Unknown'

    posts_text_for_summary = analyzer.prepare_posts_for_analysis(sorted_posts)

    prompt = f"""You are analyzing a collection of Substack essays from the author ITNAmatter (Jonathan Politzki). 
These essays span from {oldest_date_str} to {newest_date_str}.

Please provide a comprehensive summary and analysis of these essays, covering:

1.  **Main Themes and Ideas**: What are the core subjects and concepts the author explores? How do they connect?
2.  **Author's Perspective/Voice**: Describe the author's general tone, style, and any distinct viewpoints.
3.  **Key Takeaways**: What are the most significant insights or arguments presented across the essays?
4.  **Intellectual Journey**: What can you infer about the author's intellectual or personal development based on the writing?

Please synthesize this into a coherent narrative summary. Avoid just listing points; try to tell a story about the author's body of work as presented.

Here are the posts:

{posts_text_for_summary}"""
    try:
        response = analyzer.model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary with Gemini: {e}")
        return f"Error generating summary: {e}"

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Substack Analyzer AI")

st.title("Substack Essay Analyzer with Gemini AI")
st.markdown("Analyze your Substack essays to understand thematic evolution, writing style, and more, powered by Google Gemini 1.5 Pro.")

# --- Sidebar for Configuration ---
st.sidebar.header("Configuration")

# API Key Input
gemini_api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password", help="Get your key from Google AI Studio")
if gemini_api_key:
    os.environ['GEMINI_API_KEY'] = gemini_api_key # Set it for the current session
    # Attempt to initialize analyzer as soon as key is entered
    if not st.session_state.get('analyzer_instance'): 
        st.session_state.analyzer_instance = get_analyzer_instance(gemini_api_key)
else:
    st.sidebar.warning("Please enter your Gemini API key to enable analysis features.")
    st.session_state.analyzer_instance = None # Clear instance if key is removed
    st.session_state.gemini_api_key_valid = False

substack_url = st.sidebar.text_input("Your Substack URL", value="https://jonathanpolitzki.substack.com/")

if st.sidebar.button("Fetch Posts"):
    if not substack_url:
        st.sidebar.error("Please enter a Substack URL.")
    else:
        with st.spinner("Fetching posts..."):
            try:
                # Run the async function in a way Streamlit can handle
                posts_list = asyncio.run(fetch_posts_async(substack_url))
                if posts_list:
                    st.session_state.posts = posts_list
                    st.sidebar.success(f"Fetched {len(posts_list)} posts!")
                    # Clear previous analysis results when new posts are fetched
                    st.session_state.analysis_summary = None
                    st.session_state.qa_answer = None
                else:
                    st.sidebar.error("No posts found or failed to fetch.")
                    st.session_state.posts = None
            except Exception as e:
                st.sidebar.error(f"Error fetching posts: {e}")
                st.session_state.posts = None

# --- Main Content Area ---
if st.session_state.posts:
    st.header(f"Fetched {len(st.session_state.posts)} Posts")
    with st.expander("View Fetched Post Titles and Dates", expanded=False):
        for post in st.session_state.posts:
            date_display = post.date.strftime("%Y-%m-%d") if post.date else "No Date"
            st.markdown(f"- **{post.title}** ({date_display})")
    
    if st.session_state.analyzer_instance and st.session_state.gemini_api_key_valid:
        # Overall Summary Section
        st.subheader("Overall Writing Summary & Analysis")
        if st.button("Generate Overall Summary"):
            with st.spinner("Gemini is thinking about the big picture..."):
                st.session_state.analysis_summary = generate_overall_summary(st.session_state.analyzer_instance, st.session_state.posts)
        
        if st.session_state.analysis_summary:
            st.markdown(st.session_state.analysis_summary)

        # Q&A Section
        st.subheader("Ask Questions About Your Essays")
        user_question = st.text_area("Enter your question here:", height=100, 
                                     placeholder="e.g., What are my main arguments about AI? How has my view on philosophy changed over time?")
        if st.button("Ask Gemini"):
            if user_question:
                with st.spinner("Gemini is searching for answers in your essays..."):
                    st.session_state.qa_answer = ask_gemini_about_corpus(st.session_state.analyzer_instance, st.session_state.posts, user_question)
            else:
                st.warning("Please type a question.")
        
        if st.session_state.qa_answer:
            st.markdown("### Answer:")
            st.markdown(st.session_state.qa_answer)
    else:
        st.warning("Please enter a valid Gemini API key in the sidebar to enable analysis.")

else:
    st.info("Fetch posts using the sidebar to begin analysis.")

# Add a note about the RSS feed limitation
st.sidebar.markdown("---    ")
st.sidebar.info("Note: The scraper currently uses the RSS feed, which typically provides only the 20 most recent posts.") 