#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { config } from 'dotenv';

// Load environment variables
config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = dirname(__dirname);

// Server configuration
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const SUBSTACK_URL = process.env.SUBSTACK_URL || 'https://jonathanpolitzki.substack.com/';

if (!GEMINI_API_KEY) {
  console.error('Error: GEMINI_API_KEY environment variable is required');
  process.exit(1);
}

// Cache for fetched posts
let cachedPosts = null;
let cacheTimestamp = null;
const CACHE_DURATION = 60 * 60 * 1000; // 1 hour

// Helper function to run Python scripts
async function runPythonScript(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [scriptPath, ...args], {
      cwd: projectRoot,
      env: { ...process.env, GEMINI_API_KEY }
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script failed: ${stderr}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

// Create the MCP server
const server = new Server(
  {
    name: 'substack-analyzer-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'fetch_substack_posts',
        description: 'Fetch the latest posts from your Substack RSS feed',
        inputSchema: {
          type: 'object',
          properties: {
            force_refresh: {
              type: 'boolean',
              description: 'Force refresh even if cached data exists',
              default: false
            }
          }
        }
      },
      {
        name: 'analyze_writing_summary',
        description: 'Generate a comprehensive summary and analysis of your Substack essays covering themes, writing style, perspective, and intellectual journey',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      },
      {
        name: 'ask_about_writing',
        description: 'Ask a specific question about your Substack essays and get an answer based on the full text',
        inputSchema: {
          type: 'object',
          properties: {
            question: {
              type: 'string',
              description: 'The question to ask about your essays'
            }
          },
          required: ['question']
        }
      }
    ]
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'fetch_substack_posts': {
        // Check cache unless force refresh is requested
        const forceRefresh = args?.force_refresh || false;
        const now = Date.now();
        
        if (!forceRefresh && cachedPosts && cacheTimestamp && (now - cacheTimestamp < CACHE_DURATION)) {
          return {
            content: [
              {
                type: 'text',
                text: `Using cached posts (${cachedPosts.length} posts from ${new Date(cacheTimestamp).toLocaleString()}). Use force_refresh=true to fetch new posts.`
              }
            ]
          };
        }

        // Create a Python script to fetch posts
        const fetchScript = `
import asyncio
import sys
import json
sys.path.append('${projectRoot}')
from scraper import SubstackScraper

async def fetch():
    scraper = SubstackScraper('${SUBSTACK_URL}')
    posts = await scraper.scrape()
    return [{
        'title': post.title,
        'url': post.url,
        'date': post.date.isoformat() if post.date else None,
        'content': post.content
    } for post in posts]

result = asyncio.run(fetch())
print(json.dumps(result))
`;
        const scriptPath = join(projectRoot, 'temp_fetch.py');
        await fs.writeFile(scriptPath, fetchScript);
        
        try {
          const output = await runPythonScript(scriptPath);
          const posts = JSON.parse(output);
          
          // Update cache
          cachedPosts = posts;
          cacheTimestamp = Date.now();
          
          await fs.unlink(scriptPath);
          
          return {
            content: [
              {
                type: 'text',
                text: `Successfully fetched ${posts.length} posts from ${SUBSTACK_URL}\n\nPost titles:\n${posts.map(p => `- ${p.title} (${p.date ? new Date(p.date).toLocaleDateString() : 'No date'})`).join('\n')}`
              }
            ]
          };
        } catch (error) {
          await fs.unlink(scriptPath).catch(() => {});
          throw error;
        }
      }

      case 'analyze_writing_summary': {
        if (!cachedPosts || cachedPosts.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No posts loaded. Please run fetch_substack_posts first.'
              }
            ]
          };
        }

        // Save posts to a temporary file to avoid embedding large content
        const postsDataPath = join(projectRoot, 'temp_posts_data.json');
        await fs.writeFile(postsDataPath, JSON.stringify(cachedPosts));

        // Create a Python script to analyze posts
        const analyzeScript = `
import sys
import json
import os
sys.path.append('${projectRoot}')
from analyzer import SubstackAnalyzer
from datetime import datetime

# Read posts from file
with open('${postsDataPath}', 'r', encoding='utf-8') as f:
    posts_data = json.load(f)

# Convert back to post objects
class Post:
    def __init__(self, title, url, date, content):
        self.title = title
        self.url = url
        self.date = datetime.fromisoformat(date) if date else None
        self.content = content

posts = [Post(**p) for p in posts_data]

analyzer = SubstackAnalyzer(os.environ.get('GEMINI_API_KEY'))

# Sort posts by date
sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)
oldest_date_str = sorted_posts[0].date.strftime('%B %Y') if sorted_posts and sorted_posts[0].date else 'Unknown'
newest_date_str = sorted_posts[-1].date.strftime('%B %Y') if sorted_posts and sorted_posts[-1].date else 'Unknown'

posts_text = analyzer.prepare_posts_for_analysis(sorted_posts)

prompt = f"""You are analyzing a collection of Substack essays from the author ITNAmatter (Jonathan Politzki). 
These essays span from {oldest_date_str} to {newest_date_str}.

Please provide a comprehensive summary and analysis of these essays, covering:

1.  **Main Themes and Ideas**: What are the core subjects and concepts the author explores? How do they connect?
2.  **Author's Perspective/Voice**: Describe the author's general tone, style, and any distinct viewpoints.
3.  **Key Takeaways**: What are the most significant insights or arguments presented across the essays?
4.  **Intellectual Journey**: What can you infer about the author's intellectual or personal development based on the writing?

Please synthesize this into a coherent narrative summary. Avoid just listing points; try to tell a story about the author's body of work as presented.

Here are the posts:

{posts_text}"""

response = analyzer.model.generate_content(prompt)
print(response.text)
`;
        const scriptPath = join(projectRoot, 'temp_analyze.py');
        await fs.writeFile(scriptPath, analyzeScript);
        
        try {
          const output = await runPythonScript(scriptPath);
          await fs.unlink(scriptPath);
          await fs.unlink(postsDataPath);
          
          return {
            content: [
              {
                type: 'text',
                text: output.trim()
              }
            ]
          };
        } catch (error) {
          await fs.unlink(scriptPath).catch(() => {});
          await fs.unlink(postsDataPath).catch(() => {});
          throw error;
        }
      }

      case 'ask_about_writing': {
        if (!cachedPosts || cachedPosts.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No posts loaded. Please run fetch_substack_posts first.'
              }
            ]
          };
        }

        const question = args.question;
        if (!question) {
          throw new Error('Question is required');
        }

        // Save posts to a temporary file to avoid embedding large content
        const postsDataPath = join(projectRoot, 'temp_posts_data_ask.json');
        await fs.writeFile(postsDataPath, JSON.stringify(cachedPosts));

        // Create a Python script to ask questions
        const askScript = `
import sys
import json
import os
sys.path.append('${projectRoot}')
from analyzer import SubstackAnalyzer
from datetime import datetime

# Read posts from file
with open('${postsDataPath}', 'r', encoding='utf-8') as f:
    posts_data = json.load(f)

question = """${question.replace(/"/g, '\\"')}"""

# Convert back to post objects
class Post:
    def __init__(self, title, url, date, content):
        self.title = title
        self.url = url
        self.date = datetime.fromisoformat(date) if date else None
        self.content = content

posts = [Post(**p) for p in posts_data]

analyzer = SubstackAnalyzer(os.environ.get('GEMINI_API_KEY'))

# Sort posts by date
sorted_posts = sorted(posts, key=lambda p: p.date or datetime.min)

# Combine all post content
corpus_parts = []
for i, post in enumerate(sorted_posts):
    date_str = post.date.strftime("%Y-%m-%d") if post.date else "Unknown date"
    corpus_parts.append(f"--- ESSAY {i+1} ---\\nTitle: {post.title}\\nDate: {date_str}\\n\\n{post.content}\\n--- END ESSAY {i+1} ---\\n")
corpus = "\\n".join(corpus_parts)

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

response = analyzer.model.generate_content(prompt)
print(response.text)
`;
        const scriptPath = join(projectRoot, 'temp_ask.py');
        await fs.writeFile(scriptPath, askScript);
        
        try {
          const output = await runPythonScript(scriptPath);
          await fs.unlink(scriptPath);
          await fs.unlink(postsDataPath);
          
          return {
            content: [
              {
                type: 'text',
                text: output.trim()
              }
            ]
          };
        } catch (error) {
          await fs.unlink(scriptPath).catch(() => {});
          await fs.unlink(postsDataPath).catch(() => {});
          throw error;
        }
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Substack Analyzer MCP server running');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
}); 