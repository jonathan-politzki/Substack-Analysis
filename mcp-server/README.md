# Substack Analyzer MCP Server

This is an MCP (Model Context Protocol) server that allows you to analyze your Substack essays using Google's Gemini AI directly from Claude Desktop.

## Features

The MCP server exposes three tools to Claude:

1. **fetch_substack_posts** - Fetches the latest posts from your Substack RSS feed
2. **analyze_writing_summary** - Generates a comprehensive analysis of your writing covering themes, style, and intellectual journey
3. **ask_about_writing** - Ask specific questions about your essays and get answers based on the full text

## Prerequisites

- Node.js 18+ installed
- Python 3.x installed (for running the analyzer)
- A Google Gemini API key
- Claude Desktop app

## Setup Instructions

### 1. Install Dependencies

First, install the Node.js dependencies:

```bash
cd mcp-server
npm install
```

### 2. Configure Environment

Copy the example environment file and add your API key:

```bash
cp env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your-actual-api-key-here
SUBSTACK_URL=https://jonathanpolitzki.substack.com/
```

### 3. Configure Claude Desktop

You need to add this MCP server to your Claude Desktop configuration.

**On macOS:**

1. Open your Claude Desktop configuration file:
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Add the following to the `mcpServers` section (create it if it doesn't exist):
   ```json
   {
     "mcpServers": {
       "substack-analyzer": {
         "command": "node",
         "args": [
           "/Users/jonathanpolitzki/Desktop/Coding/Substack-Analysis/mcp-server/index.js"
         ],
         "env": {
           "GEMINI_API_KEY": "your-actual-gemini-api-key",
           "SUBSTACK_URL": "https://jonathanpolitzki.substack.com/"
         }
       }
     }
   }
   ```

   Make sure to:
   - Replace the path with the absolute path to your `mcp-server/index.js` file
   - Add your actual Gemini API key
   - Update the Substack URL if needed

3. Restart Claude Desktop for the changes to take effect

**On Windows:**

The config file is located at:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 4. Test the Server

You can test the server standalone:

```bash
node index.js
```

It should output: `Substack Analyzer MCP server running`

## Using in Claude

Once configured, you can use these commands in Claude:

1. **Fetch your posts:**
   - "Fetch my Substack posts"
   - "Get the latest posts from my Substack"

2. **Analyze your writing:**
   - "Analyze my Substack writing and give me a summary"
   - "What are the main themes in my essays?"

3. **Ask questions:**
   - "What have I written about AI?"
   - "Summarize my thoughts on technology"
   - "How has my writing style evolved?"

## How It Works

The MCP server:
1. Uses the existing Python scraper and analyzer code
2. Spawns Python processes to run the analysis
3. Caches fetched posts for 1 hour to avoid repeated API calls
4. Returns results to Claude in a structured format

## Troubleshooting

### "Python script failed" errors
- Make sure Python 3 is installed and accessible as `python3`
- Ensure all Python dependencies are installed in the parent directory:
  ```bash
  cd ..
  pip install -r requirements.txt
  ```

### "GEMINI_API_KEY environment variable is required"
- Make sure you've set up your `.env` file or added the API key to the Claude config

### Claude doesn't see the tools
- Restart Claude Desktop after updating the configuration
- Check that the path in the config file is absolute and correct
- Verify the MCP server starts without errors

## Development

To run in development mode with auto-reload:

```bash
npm run dev
```

## Notes

- The server caches posts for 1 hour. Use `force_refresh: true` to bypass the cache
- RSS feeds typically only provide the ~20 most recent posts
- All analysis is done using Google's Gemini AI, so API usage costs apply 