#!/usr/bin/env node

import prompts from 'prompts';
import chalk from 'chalk';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { spawn } from 'child_process';
import os from 'os';

// Add fetch for Node.js versions that don't have it built-in
const fetch = globalThis.fetch || (await import('node-fetch')).default;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ASCII art banner
const banner = `
╔════════════════════════════════════════════╗
║     ${chalk.cyan('Substack Analysis MCP Setup')}         ║
║  ${chalk.gray('Analyze your writing with Gemini AI')}    ║
╚════════════════════════════════════════════╝
`;

// Get Claude Desktop config path based on OS
function getClaudeConfigPath() {
  const platform = os.platform();
  const homeDir = os.homedir();
  
  switch (platform) {
    case 'darwin': // macOS
      return path.join(homeDir, 'Library', 'Application Support', 'Claude', 'claude_desktop_config.json');
    case 'win32': // Windows
      return path.join(process.env.APPDATA || path.join(homeDir, 'AppData', 'Roaming'), 'Claude', 'claude_desktop_config.json');
    case 'linux':
      return path.join(homeDir, '.config', 'Claude', 'claude_desktop_config.json');
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}

// Validate Substack URL
function validateSubstackUrl(url) {
  if (!url) return 'Substack URL is required';
  
  // Accept various formats
  const patterns = [
    /^https?:\/\/[\w-]+\.substack\.com\/?$/,
    /^[\w-]+\.substack\.com\/?$/,
    /^[\w-]+$/
  ];
  
  if (patterns.some(pattern => pattern.test(url))) {
    return true;
  }
  
  return 'Please enter a valid Substack URL or username';
}

// Format Substack URL
function formatSubstackUrl(input) {
  // If it's just a username, format it
  if (/^[\w-]+$/.test(input)) {
    return `https://${input}.substack.com/`;
  }
  
  // If it's missing https://, add it
  if (/^[\w-]+\.substack\.com\/?$/.test(input)) {
    return `https://${input}`;
  }
  
  // Ensure trailing slash
  if (!input.endsWith('/')) {
    return `${input}/`;
  }
  
  return input;
}

// Check if Python and pip are installed
async function checkPythonDependencies() {
  try {
    await new Promise((resolve, reject) => {
      const pythonCheck = spawn('python3', ['--version'], { shell: true });
      pythonCheck.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error('Python 3 not found'));
      });
    });
    
    await new Promise((resolve, reject) => {
      const pipCheck = spawn('pip3', ['--version'], { shell: true });
      pipCheck.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error('pip3 not found'));
      });
    });
    
    return true;
  } catch (error) {
    return false;
  }
}

// Download Python files from GitHub
async function downloadPythonFiles(installDir) {
  const baseUrl = 'https://raw.githubusercontent.com/jonathan-politzki/Substack-Analysis/main';
  const files = [
    { name: 'scraper.py', url: `${baseUrl}/scraper.py` },
    { name: 'analyzer.py', url: `${baseUrl}/analyzer.py` },
    { name: 'requirements.txt', url: `${baseUrl}/requirements.txt` }
  ];

  console.log(chalk.cyan('📥 Downloading Python components...'));
  
  for (const file of files) {
    try {
      console.log(chalk.gray(`Downloading ${file.name} from ${file.url}...`));
      const response = await fetch(file.url);
      if (!response.ok) {
        throw new Error(`Failed to download ${file.name}: ${response.statusText}`);
      }
      const content = await response.text();
      await fs.writeFile(path.join(installDir, file.name), content);
      console.log(chalk.green(`✓ Downloaded ${file.name}`));
    } catch (error) {
      console.log(chalk.yellow(`⚠ Could not download ${file.name}: ${error.message}`));
      // Fallback: try to copy from current directory if available
      try {
        const sourcePath = path.join(__dirname, file.name);
        const destPath = path.join(installDir, file.name);
        await fs.copyFile(sourcePath, destPath);
        console.log(chalk.gray(`✓ Copied ${file.name} from package`));
      } catch (copyError) {
        console.error(chalk.red(`✗ Failed to get ${file.name}: ${error.message}`));
        throw new Error(`Cannot install without ${file.name}`);
      }
    }
  }
}

// Main setup function
async function setup() {
  console.clear();
  console.log(banner);
  
  console.log(chalk.yellow('Welcome! Let\'s set up your Substack Analysis for Claude Desktop.\n'));
  
  // Check Python dependencies
  console.log(chalk.cyan('🐍 Checking Python dependencies...'));
  const hasPython = await checkPythonDependencies();
  
  if (!hasPython) {
    console.log(chalk.red('\n✗ Python 3 and pip3 are required but not found.'));
    console.log(chalk.yellow('Please install Python 3 from https://www.python.org/downloads/'));
    process.exit(1);
  }
  console.log(chalk.green('✓ Python 3 and pip3 found'));
  
  // Check if running via npx or locally
  const isNpx = process.env.npm_execpath && process.env.npm_execpath.includes('npx') || 
                __dirname.includes('.npm/_npx') || 
                __dirname.includes('node_modules');
  
  console.log(chalk.gray(`Detection: isNpx=${isNpx}, __dirname=${__dirname}`));
  
  // Prompt for configuration
  const questions = [
    {
      type: 'text',
      name: 'substackUrl',
      message: 'Enter your Substack URL or username:',
      initial: 'username',
      validate: validateSubstackUrl,
      format: formatSubstackUrl
    },
    {
      type: 'password',
      name: 'geminiApiKey',
      message: 'Enter your Gemini API key:',
      validate: value => value ? true : 'Gemini API key is required'
    }
  ];
  
  const answers = await prompts(questions);
  
  if (!answers.substackUrl || !answers.geminiApiKey) {
    console.log(chalk.red('\n✗ Setup cancelled'));
    process.exit(1);
  }
  
  console.log(chalk.cyan('\n📦 Installing MCP server...'));
  
  // Determine installation directory
  let installDir;
  const projectRoot = path.dirname(__dirname);
  
  if (isNpx) {
    // Install in user's home directory for npx
    installDir = path.join(os.homedir(), '.mcp-servers', 'substack-analysis');
    console.log(chalk.gray(`Installing to: ${installDir}`));
    
    // Create directory
    await fs.mkdir(installDir, { recursive: true });
    
    // Copy necessary files from npm package
    const filesToCopy = [
      { src: 'index.js', dest: 'index.js' },
      { src: 'package.json', dest: 'package.json' },
      { src: 'README.md', dest: 'README.md' }
    ];
    
    for (const file of filesToCopy) {
      const sourcePath = path.join(__dirname, file.src);
      const destPath = path.join(installDir, file.dest);
      
      try {
        await fs.copyFile(sourcePath, destPath);
      } catch (error) {
        console.error(chalk.red(`Failed to copy ${file.src}: ${error.message}`));
      }
    }
    
    // Download Python files from GitHub
    await downloadPythonFiles(installDir);
    
    // Install Node dependencies
    console.log(chalk.cyan('📥 Installing Node.js dependencies...'));
    await new Promise((resolve, reject) => {
      const install = spawn('npm', ['install', '--production'], {
        cwd: installDir,
        shell: true,
        stdio: 'inherit'
      });
      
      install.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`npm install failed with code ${code}`));
      });
    });
    
    // Install Python dependencies
    console.log(chalk.cyan('📥 Installing Python dependencies...'));
    await new Promise((resolve, reject) => {
      const pipInstall = spawn('pip3', ['install', '-r', 'requirements.txt'], {
        cwd: installDir,
        shell: true,
        stdio: 'inherit'
      });
      
      pipInstall.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`pip install failed with code ${code}`));
      });
    });
  } else {
    // Use project root directory if running locally
    installDir = projectRoot;
    
    // Install Node dependencies if needed
    console.log(chalk.cyan('📥 Installing dependencies...'));
    await new Promise((resolve, reject) => {
      const install = spawn('npm', ['install'], {
        cwd: __dirname,
        shell: true,
        stdio: 'inherit'
      });
      
      install.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`npm install failed with code ${code}`));
      });
    });
  }
  
  // Create .env file in MCP server directory
  const envPath = isNpx ? path.join(installDir, '.env') : path.join(__dirname, '.env');
  const envContent = `# Substack Analysis MCP Configuration
GEMINI_API_KEY=${answers.geminiApiKey}
SUBSTACK_URL=${answers.substackUrl}
`;
  
  await fs.writeFile(envPath, envContent);
  console.log(chalk.green('✓ Created .env file'));
  
  // Update Claude Desktop config
  console.log(chalk.cyan('\n🔧 Updating Claude Desktop configuration...'));
  
  const configPath = getClaudeConfigPath();
  let config = {};
  
  try {
    const configContent = await fs.readFile(configPath, 'utf-8');
    config = JSON.parse(configContent);
  } catch (error) {
    console.log(chalk.yellow('No existing Claude config found, creating new one...'));
  }
  
  // Ensure mcpServers object exists
  if (!config.mcpServers) {
    config.mcpServers = {};
  }
  
  // Add or update our server configuration
  const mcpIndexPath = isNpx ? path.join(installDir, 'index.js') : path.join(__dirname, 'index.js');
  
  config.mcpServers['substack-analysis'] = {
    command: 'node',
    args: [mcpIndexPath],
    env: {
      GEMINI_API_KEY: answers.geminiApiKey,
      SUBSTACK_URL: answers.substackUrl
    }
  };
  
  // Ensure config directory exists
  const configDir = path.dirname(configPath);
  await fs.mkdir(configDir, { recursive: true });
  
  // Write updated config
  await fs.writeFile(configPath, JSON.stringify(config, null, 2));
  console.log(chalk.green('✓ Updated Claude Desktop configuration'));
  
  // Success message
  console.log(chalk.green('\n✨ Setup complete!\n'));
  console.log(chalk.white('The Substack Analysis MCP server has been configured.'));
  console.log(chalk.white('\nNext steps:'));
  console.log(chalk.cyan('1. Restart Claude Desktop'));
  console.log(chalk.cyan('2. You can now use these commands:'));
  console.log(chalk.gray('   - "Fetch my Substack posts"'));
  console.log(chalk.gray('   - "Analyze my writing"'));
  console.log(chalk.gray('   - "What have I written about [topic]?"'));
  
  console.log(chalk.gray(`\n📁 Server installed at: ${installDir}`));
  console.log(chalk.gray(`📝 Config file: ${configPath}\n`));
}

// Run setup with error handling
setup().catch(error => {
  console.error(chalk.red('\n✗ Setup failed:'), error.message);
  process.exit(1);
}); 