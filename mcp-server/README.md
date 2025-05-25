# Substack Analysis MCP Server for Claude Desktop

This tool allows you to analyze your Substack essays using Gemini AI, directly within Claude Desktop. It fetches your posts, summarizes your writing, and answers specific questions about your content.

## Quick Start

1.  **Ensure Prerequisites:**
    *   Node.js (v18.0.0 or higher)
    *   Python 3
    *   pip3 (Python package installer)
    *   A Google Gemini API Key
    *   Your Substack URL (e.g., `https://yourname.substack.com/`)

2.  **Install & Configure:**
    Run this command in your terminal:
    ```bash
    npx substack-analysis-mcp@latest
    ```
    The interactive setup will guide you through providing your Substack URL and Gemini API Key. It will also automatically check for Python/pip and configure Claude Desktop.

3.  **Restart Claude Desktop:**
    After the setup completes, restart your Claude Desktop application.

## Available Tools

Once installed and Claude Desktop is restarted, you can use these commands:

*   **Fetch your Substack posts:**
    *   Example: `Fetch my Substack posts`
    *   Optional: `Fetch my Substack posts (force refresh)` or send `{ "force_refresh": true }` to ignore the 1-hour cache.

*   **Analyze your writing:**
    *   Example: `Analyze my writing`
    *   This provides a comprehensive summary of themes, style, and intellectual journey.

*   **Ask about your writing:**
    *   Example: `What have I written about Politzki's Law?`
    *   Pass your question directly or use the input field: `{ "question": "Your question here" }`

## How It Works

The `npx substack-analysis-mcp@latest` command downloads and runs a setup script. This script:
1.  Copies the MCP server (including Python scripts for scraping and AI analysis) to a local directory.
2.  Prompts you for your Substack URL and Gemini API Key.
3.  Saves these as environment variables for the server.
4.  Automatically updates your Claude Desktop configuration to recognize these new tools.

The server then uses Python and your Gemini API key to process your Substack content when you invoke the tools in Claude.

## Troubleshooting

*   **`ModuleNotFoundError` (e.g., no module named 'scraper'):**
    *   This usually means the Python scripts were not correctly placed or their dependencies weren't installed. Version `1.0.8+` should have resolved this by bundling all necessary files. Ensure you are using the latest version: `npx substack-analysis-mcp@latest`.
    *   Verify Python 3 and pip3 are correctly installed and in your system's PATH.
*   **Claude doesn't see the tools:**
    *   Ensure you restarted Claude Desktop after the setup script completed.
    *   Check the `claude_desktop_config.json` file (path shown at the end of setup) to see if the `substack-analysis` server is listed under `mcpServers`.
*   **Other errors:** The setup script or MCP server will output error messages to the console. These can help diagnose issues with API keys, Substack URLs, or Python execution. 