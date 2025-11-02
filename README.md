# Mate
_Sipping knowledge with your agentic studdybuddy_

Mate provides an all-in-one study environment designed to help you get the most out of your study sessions. It anticipates your needs and recommends relevant pages or resources based on your recent activity.

## Setup

### 1. Install Python
Make sure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
Open a terminal in this directory and run:
```bash
pip install -r requirements.txt
```

### 3. Add Your Anthropic API Key
1. Get your API key from: https://console.anthropic.com/
2. Create a folder named `api_key` in the project root
3. Create a file `api_key.txt` inside that folder
4. Paste your API key into `api_key.txt` (just the key, no quotes or extra formatting)

Example file content (`api_key/api_key.txt`):
```
sk-ant-api03-...
```

### 4. (Optional) Customize Settings
You can customize the app behavior by editing `config.py`:

**Window Size**: Set minimum and maximum window dimensions
```python
WINDOW_MIN_WIDTH = 400   # Minimum window width
WINDOW_MAX_WIDTH = 600   # Maximum window width
WINDOW_MIN_HEIGHT = 200  # Minimum window height
WINDOW_MAX_HEIGHT = 700  # Maximum window height
```

**Window Position**: Adjust where the explanation window appears (distance from bottom-right corner)
```python
WINDOW_MARGIN_RIGHT = 100  # Pixels from right edge
WINDOW_MARGIN_BOTTOM = 200  # Pixels from bottom edge
```

### 5. Run the Application
```bash
python main.py
```

## How to Use

1. **Launch the app** - Run `python main.py` and a purple-blue "mate" button will appear in the bottom right
2. Go studying and focus on what's important
3. **Highlight any text and click the button** – An explanation window will instantly appear with helpful information.
4. **Start a Pomodoro timer** – Click the button to begin a focused Pomodoro study session.
5. **Get personalized study suggestions** – The AI monitors your work and recommends the next best resources to explore.
6. **Snapshot Your Study Session**  - At any time, click the "+" button in the menu to instantly generate a concise summary of everything you've studied during the session – including key topics, definitions, and main ideas. The summary appears in a new window and can be copied for your notes or revision.


## Features

- **Draggable Button**: Hold and drag the button to reposition it
- **Always On Top**: The button stays visible over all applications
- **Smart Explanations**: 
  - Single words/short phrases: Gets a definition
  - Longer text: Gets a simplified version
- **Prediction Feature**: Instantly predicts what you're studying (topic or concept) and offers tailored explanations
- **Pomodoro Timer**: Built-in Pomodoro timer to help structure your study sessions and maintain focus
- **Snapshot**: Summarizes your entire study session at any time, giving you a concise overview of what you've covered and key points learned
- **Modern UI**: Clean, minimalist explanation window with **rounded corners** and smooth hover effects
- **Responsive Sizing**: Window automatically adapts to content size (configurable min/max bounds)
- **Configurable Positioning**: Adjust window position via `WINDOW_MARGIN_RIGHT` and `WINDOW_MARGIN_BOTTOM` in config.py
- **Markdown Support**: Full markdown rendering with headers, bold, italic, code, links, and bullet points
- **Hybrid UI**: CustomTkinter for modern window styling + native Text widget for rich markdown formatting
- **Customizable**: Edit `config.py` to change button size, prompts, and AI model

## Troubleshooting

- **"Please set your Anthropic API key"**: Make sure you've created `api_key/api_key.txt` with your API key
- **Button not visible**: Check if it's behind the taskbar; try dragging it up
- **No text copied**: Make sure to select text before clicking the button

## Requirements

- Windows 10/11, Linux, MacOS
- Python 3.8+
- Anthropic API key

