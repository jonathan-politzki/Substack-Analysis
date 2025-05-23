# Substack Analyzer

This repository contains scripts to fetch Substack posts from a given URL, store them, and provides a framework for analyzing them (e.g., using Gemini).

## Setup

1.  **Clone the repository (or create the files as described):**
    ```bash
    # If this were a git repo, you'd clone it.
    # For now, ensure you have main.py, scraper.py, and requirements.txt
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

-   Open `main.py`.
-   Modify the `SUBSTACK_URL` variable to point to your Substack blog URL if different from the default.
    ```python
    SUBSTACK_URL = "https://yourusername.substack.com/"
    ```
-   You can also adjust `MAX_POSTS_TO_FETCH` if needed.

## Running the Scraper

To fetch (or re-fetch) posts and save them to `substack_data/substack_posts.json`:

```bash
python main.py
```

The script will first try to load posts from the JSON file. If the file doesn't exist or is empty, it will then fetch posts from Substack.
To force a refetch, delete the `substack_data/substack_posts.json` file before running the script.

## Data

-   Fetched posts are stored in `substack_data/substack_posts.json`.
-   Each post includes its title, URL, content, date, and subtitle (if available).

## Analysis with Gemini (Placeholder)

The `main.py` script includes a placeholder function `analyze_posts_with_gemini(posts)`.
To implement the analysis:

1.  **Install the Gemini library:**
    ```bash
    pip install google-generativeai
    ```
    (Uncomment it in `requirements.txt` as well if you plan to re-install dependencies later)

2.  **Update `analyze_posts_with_gemini` in `main.py`:**
    -   Add your Gemini API key and authentication logic.
    -   Prepare the post data (e.g., combine content, create specific prompts).
    -   Make calls to the Gemini API.
    -   Process and store or display the analysis results.

    Refer to the comments within the function for more detailed guidance.

## Project Structure

```
. 
├── main.py             # Main script to run scraper and analysis
├── scraper.py          # Contains the SubstackScraper class
├── requirements.txt    # Python dependencies
├── substack_data/      # Directory to store fetched data (created automatically)
│   └── substack_posts.json # Saved posts data
└── README.md           # This file
```
