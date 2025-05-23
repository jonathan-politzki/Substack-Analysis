# Substack Analyzer

This repository contains scripts to fetch Substack posts from a given URL, store them, analyze them using Google's Gemini AI, and create visualizations of writing patterns over time.

## Features

- 📥 Fetches posts from any Substack RSS feed
- 💾 Stores posts locally in JSON format
- 📊 Generates statistics and visualizations
- 🤖 Analyzes writing evolution using Gemini AI
- 🎯 Tracks themes and patterns over time

## Setup

1.  **Clone the repository (or create the files as described):**
    ```bash
    git clone <repository-url>
    cd Substack-Analysis
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

4.  **Set up Gemini API key:**
    - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    - Create a `.env` file in the project root:
      ```
      GEMINI_API_KEY=your-api-key-here
      ```
    - Or export it as an environment variable:
      ```bash
      export GEMINI_API_KEY='your-api-key-here'
      ```

## Configuration

-   Open `main.py` and modify the `SUBSTACK_URL` variable if needed:
    ```python
    SUBSTACK_URL = "https://yourusername.substack.com/"
    ```

## Usage

Run the main script:
```bash
python3 main.py
```

The script will:
1. Fetch posts from the Substack RSS feed (limited to 20 most recent)
2. Save them to `substack_data/substack_posts.json`
3. Generate statistics and visualizations
4. Use Gemini to analyze:
   - Writing evolution over time
   - Theme development
   - Style changes
   - Personal/professional growth
5. Save analysis results to `substack_data/analysis_results.json`

## Output Files

- `substack_data/substack_posts.json` - Raw post data
- `substack_data/substack_analysis.png` - Visualization charts
- `substack_data/analysis_results.json` - Gemini analysis results

## Limitations

- RSS feeds typically only provide the 20 most recent posts
- To analyze all posts, you may need to export from Substack's dashboard

## Customization

### Analyzing Different Themes

Edit the themes list in `main.py`:
```python
themes = ["technology", "AI", "entrepreneurship", "personal growth", "philosophy", "startup"]
```

### Adjusting Visualizations

Modify the `create_visualizations()` method in `analyzer.py` to customize charts.

## Troubleshooting

- **SSL Certificate Error**: The scraper disables SSL verification. For production use, consider proper certificate handling.
- **No posts found**: Check that the Substack URL is correct and publicly accessible.
- **Gemini API errors**: Ensure your API key is valid and you haven't exceeded rate limits.

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
