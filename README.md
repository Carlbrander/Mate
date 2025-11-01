# ELI5 Overlay - Explain Like I'm 5

A transparent overlay application that helps you understand complex text by providing simplified explanations using Claude AI.

## Features

- **Floating Button**: A semi-transparent button that stays on top of all windows in the bottom right corner
- **Auto-Copy**: Automatically copies selected text when you click the button
- **AI-Powered Explanations**: Uses Claude AI to simplify text or explain terms
- **Easy to Use**: Select text anywhere on your computer, click the button, and get instant explanations

## Setup

### 1. Install Python
Make sure you have Python 3.8+ installed on your Windows machine.

### 2. Install Dependencies
Open PowerShell in this directory and run:
```powershell
pip install -r requirements.txt
```

### 3. Add Your Anthropic API Key
1. Open `config.py`
2. Replace `"your-api-key-here"` with your actual Anthropic API key
3. Get your API key from: https://console.anthropic.com/

Example:
```python
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

### 4. (Optional) Customize the Prompt
You can customize how Claude responds by editing `PROMPT_TEMPLATE` in `config.py`. The `{text}` placeholder will be replaced with your selected text.

Example:
```python
PROMPT_TEMPLATE = """You are a helpful coding assistant.

Code/Text:
{text}

Please explain this in detail with examples."""
```

### 5. Run the Application
```powershell
python main.py
```

The terminal will display:
- The prompt sent to Claude
- The response received
- Status messages

## How to Use

1. **Launch the app** - Run `python main.py` and a purple-blue "mate" button will appear in the bottom right
2. **Select any text** - Highlight text anywhere on your computer (browser, Word, PDF, etc.)
3. **Click the button** - Click the mate button to explain the selected text
4. **Read explanation** - A compact window with rounded corners appears in the top-right (1/5 width × 60% height)
5. **Close** - Click the large X button in the top right to close the explanation window

## Features

- **Draggable Button**: Hold and drag the button to reposition it
- **Always On Top**: The button stays visible over all applications
- **Smart Explanations**: 
  - Single words/short phrases: Gets a definition
  - Longer text: Gets a simplified version
- **Modern UI**: Clean, minimalist explanation window with **rounded corners** and smooth hover effects
- **Responsive Sizing**: Compact window that scales to your screen resolution (1/5 width × 60% height)
- **Smart Positioning**: Top-right corner placement with margins to prevent cutoff
- **Markdown Support**: Full markdown rendering with headers, bold, italic, code, links, and bullet points
- **Hybrid UI**: CustomTkinter for modern window styling + native Text widget for rich markdown formatting
- **Customizable**: Edit `config.py` to change button size, prompts, and AI model

## Troubleshooting

- **"Please set your Anthropic API key"**: Make sure you've added your API key to `config.py`
- **Button not visible**: Check if it's behind the taskbar; try dragging it up
- **No text copied**: Make sure to select text before clicking the button

## Requirements

- Windows 10/11
- Python 3.8+
- Anthropic API key

