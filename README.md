# Substack Essay Analyzer AI

This tool fetches your Substack essays, analyzes them using Google's Gemini AI (specifically `gemini-2.5-pro-preview-05-06`), and provides an interactive web interface to explore insights about your writing.

## Features

-   **Interactive Web UI**: Built with Streamlit for easy use.
-   **Substack Scraper**: Fetches the most recent posts from your Substack RSS feed.
-   **Gemini Powered Analysis**:
    -   **Overall Summary**: Get a comprehensive analysis of themes, writing style, author's perspective, key takeaways, and inferred intellectual journey.
    -   **Interactive Q&A**: Ask specific questions about the content of your essays and get answers from Gemini based on the full text.
-   **Secure API Key Handling**: Uses environment variables (via a `.env` file or system export) for your Gemini API key.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd Substack-Analysis
    ```

2.  **Create a Python Virtual Environment (Recommended):**
    This isolates project dependencies.
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On macOS/Linux
    # For Windows: venv\Scripts\activate
    ```
    *If you don't see `(venv)` at the start of your terminal prompt, the virtual environment is not active.*

3.  **Install Dependencies:**
    Make sure your virtual environment is active, then run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Your Gemini API Key:**
    You need a Gemini API key from Google AI Studio.
    *   Go to [Google AI Studio (makersuite.google.com)](https://makersuite.google.com/app/apikey) to generate an API key.
    *   Ensure your Google Cloud Project associated with the API key has the **"Generative Language API"** and **"Vertex AI API"** enabled.
    *   Verify that billing is enabled for the project to use models like Gemini 1.5/2.5 Pro beyond very limited free tier quotas.

    Next, create a file named `.env` in the root of the project directory (`Substack-Analysis/.env`). Add your API key to this file like so:
    ```env
    GEMINI_API_KEY="your-actual-api-key-here"
    ```
    Replace `"your-actual-api-key-here"` with the API key you obtained.
    *Alternatively, you can set it as a system environment variable, e.g., `export GEMINI_API_KEY="your-actual-api-key-here"` on macOS/Linux.*

## How to Run the Application

1.  **Activate Virtual Environment (if you created one):**
    ```bash
    source venv/bin/activate
    ```

2.  **Run the Streamlit App:**
    From the project's root directory (`Substack-Analysis`), execute:
    ```bash
    streamlit run app.py
    ```
    Or, if the `streamlit` command isn't found directly (due to PATH issues):
    ```bash
    python3 -m streamlit run app.py
    ```
    This will start a local web server, and the application should open automatically in your web browser (usually at `http://localhost:8501`).

## Using the Application

1.  **Configuration (Sidebar):**
    *   **Enter your Gemini API Key**: If you haven't used a `.env` file, you can paste your API key here. The app will confirm if the key allows for analyzer initialization.
    *   **Your Substack URL**: Enter the main URL of your Substack (e.g., `https://yourname.substack.com/`).

2.  **Fetch Posts:**
    *   Click the "Fetch Posts" button in the sidebar. The app will scrape the latest posts from your Substack's RSS feed.
    *   A list of fetched post titles and dates will appear, and you can expand it to view them.

3.  **Analyze Your Essays (Requires a valid API Key):**
    *   **Overall Writing Summary & Analysis**: Click "Generate Overall Summary". Gemini will read through all fetched essays and provide a comprehensive analysis. This may take a few moments.
    *   **Ask Questions About Your Essays**: Type any question about your essays into the text area (e.g., "What are my main arguments about technology?", "Summarize my post titled 'Reflections on X'"). Click "Ask Gemini". The AI will answer based on the content of *all* fetched essays.

## Output

-   The analysis and Q&A results are displayed directly in the web application.
-   Currently, fetched posts and analysis results are not saved to disk by the Streamlit app (this was a feature of the `main.py` script). This can be added if desired.

## Important Notes & Limitations

-   **RSS Feed Limit**: Substack RSS feeds typically only provide the ~20 most recent posts. The application currently relies on this feed. To analyze your entire archive, you would need to explore methods like manual export from your Substack dashboard and adapt the tool to read that data.
-   **Gemini API Quotas**: While `gemini-2.5-pro-preview-05-06` supports a very long context, be mindful of API usage costs and potential rate limits depending on your Google Cloud/AI Studio account tier. Ensure your project has billing enabled for sustained use.
-   **Error Handling**: The application includes basic error handling for API key issues and fetching problems. If you encounter persistent errors, check your API key validity, Google Cloud project settings, and internet connection. The terminal where you ran `streamlit run app.py` will often show more detailed error logs (like the `Illegal header value` errors we troubleshooted).

## Troubleshooting Common Issues

-   **`streamlit: command not found`**:
    *   Ensure your virtual environment is active (`source venv/bin/activate`).
    *   Try running with `python3 -m streamlit run app.py`.
    *   If it persists, ensure Streamlit was installed correctly (`pip install streamlit`).
-   **Gemini API Errors (e.g., 429 Quota Exceeded, Authentication Errors, Illegal Header Value):**
    *   Verify your `GEMINI_API_KEY` is correct in the `.env` file or sidebar.
    *   Confirm "Generative Language API" and "Vertex AI API" are enabled in your Google Cloud Project.
    *   Ensure your Google Cloud Project has billing enabled and is in good standing.
    *   Check for any restrictions on your API key in the Google Cloud Console.
    *   Allow a few minutes after creating/modifying an API key or enabling services for changes to propagate.
-   **No Posts Fetched**:
    *   Double-check the Substack URL for typos.
    *   Ensure the Substack is public and its RSS feed is accessible.

## Project Structure
```
.
├── app.py              # Main Streamlit application file
├── scraper.py          # Contains the SubstackScraper class
├── analyzer.py         # Contains the SubstackAnalyzer class for Gemini AI
├── requirements.txt    # Python dependencies
├── .env.example        # (Illustrative) Example for .env file structure
└── README.md           # This file
```
*(Note: `main.py`, `substack_data/` directory, and its JSON/image outputs are part of the previous script-based version and are not directly used by the `app.py` Streamlit application unless you re-integrate those features.)*
