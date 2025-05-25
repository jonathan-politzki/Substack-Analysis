# Substack Analysis AI

This project provides tools to fetch and analyze your Substack essays using Google's Gemini AI. It can be used in two main ways:

1.  **As a set of tools directly within Claude Desktop** (Recommended).
2.  As a standalone Python application with a Streamlit web UI (using Docker).

## 🚀 Recommended: Claude Desktop Integration via MCP Server

The easiest and most integrated way to use the Substack Analysis tools is via the MCP (Model Context Protocol) server in Claude Desktop.

**Quick Installation:**

Run this single command in your terminal:

```bash
npx substack-analysis-mcp@latest
```

**What this does:**
*   Checks for necessary prerequisites (Node.js, Python 3, pip3).
*   Prompts you for your Substack URL and Gemini API Key.
*   Installs the MCP server and all dependencies (including Python scripts for scraping and analysis) to a local directory.
*   Automatically configures Claude Desktop to use these new tools.

**After Installation:**
1.  Restart Claude Desktop.
2.  You can now use commands like:
    *   `Fetch my Substack posts`
    *   `Analyze my writing`
    *   `What have I written about AI?`

For more details on the available tools, their parameters, and troubleshooting, please see the [MCP Server README](./mcp-server/README.md).

**Prerequisites for MCP Installation:**
*   Node.js (v18.0.0 or higher)
*   Python 3
*   pip3 (Python package installer)
*   A [Google Gemini API Key](https://makersuite.google.com/app/apikey)
*   Your Substack URL (e.g., `https://yourname.substack.com/`)

---

## Alternative: Dockerized Streamlit Web UI

If you prefer a standalone web interface or want to interact directly with the Python components, you can run the original Streamlit application using Docker.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/jonathan-politzki/Substack-Analysis.git
    cd Substack-Analysis
    ```

2.  **Set Up Environment:**
    Copy the example environment file and add your Gemini API Key:
    ```bash
    cp env.example .env
    ```
    Edit `.env` to add your `GEMINI_API_KEY`.

3.  **Run with Docker:**
    Ensure Docker Desktop is running, then:
    ```bash
    ./run-docker.sh
    ```
    Or manually:
    ```bash
    docker-compose up --build
    ```

4.  **Access:** Open `http://localhost:8501` in your browser.

To stop: `docker-compose down`

---

## Core Python Components

This project includes:
*   `scraper.py`: A Python script to fetch and parse Substack RSS feeds.
*   `analyzer.py`: A Python script that uses the Gemini API to perform analysis (summarization, Q&A) on the fetched essay content.
*   `app.py`: The Streamlit web application (used in the Docker setup).

These can be used independently if desired. See `requirements.txt` for Python dependencies.

## Development

If you wish to contribute or modify the code:

*   **MCP Server**: See `mcp-server/README.md`.
*   **Python Components/Streamlit App**: Ensure Python 3 and pip are installed. Create a virtual environment, install `requirements.txt`, and set your `GEMINI_API_KEY` environment variable.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    export GEMINI_API_KEY="your-key-here"
    # To run the Streamlit app:
    # streamlit run app.py
    ```

## License

MIT
