# Configuration file for ELI5 Overlay App

# Add your Anthropic API key here
ANTHROPIC_API_KEY = open("api_key/api_key.txt", "r").read().strip()

# Claude model to use
CLAUDE_MODEL = "claude-sonnet-4-5"

# Prompt settings
# {text} will be replaced with the selected text
PROMPT_TEMPLATE = """You are a helpful assistant that explains things clearly and simply.
Keep your explanations short and to the point.

Selected text:
{text}

Please provide a clear, simplified explanation of the above text. If it's a single word or short phrase, explain what it means. If it's longer text, simplify and explain it in easy-to-understand terms."""

# Button settings
BUTTON_TEXT = "mate"
BUTTON_SIZE = 160  # Circular button diameter

# Window settings (Note: Window size is now calculated dynamically as 1/4 screen width × 1/2 screen height)
# These values are kept for backward compatibility but not currently used
EXPLANATION_WINDOW_WIDTH = 1400  # Not used - calculated dynamically
EXPLANATION_WINDOW_HEIGHT = 1400  # Not used - calculated dynamically

