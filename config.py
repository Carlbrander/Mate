# Configuration file for ELI5 Overlay App

# Add your Anthropic API key here
ANTHROPIC_API_KEY = open("api_key/api_key.txt", "r").read().strip()

# Claude model to use
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Prompt settings
# {text} will be replaced with the selected text
PROMPT_TEMPLATE = """You are a helpful assistant that explains things clearly and simply.
Keep your explanations short and to the point.

Selected text:
{text}

Please provide a clear, simplified explanation of the above text. If it's a single word or short phrase, explain what it means. If it's longer text, simplify and explain it in easy-to-understand terms.
Do not include any question back to the user. Do not include a title. Just provide the markdown formatted short explanation between 100 and 300 characters.."""

# Button settings
BUTTON_TEXT = "mate"
BUTTON_SIZE = 160  # Circular button diameter

# Window settings
# Window size adapts to content but respects min/max bounds

# Window size constraints
WINDOW_MIN_WIDTH = 300  # Minimum window width in pixels
WINDOW_MAX_WIDTH = 500  # Maximum window width in pixels
WINDOW_MIN_HEIGHT = 350  # Minimum window height in pixels

WINDOW_MAX_HEIGHT = 700  # Maximum window height in pixels

# Window positioning - distance from bottom-right corner of screen
WINDOW_MARGIN_RIGHT = 1100  # Pixels from right edge of screen


WINDOW_MARGIN_BOTTOM = 1000  # Pixels from bottom edge of screen

