# Configuration file for ELI5 Overlay App

# Add your Anthropic API key here
ANTHROPIC_API_KEY = open("api_key/api_key.txt", "r").read().strip()

# Claude model to use
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

# Prompt settings
# {text} will be replaced with the selected text
CLAUDE_ROLE = "You are a helpful assistant that explains things clearly and simply. Keep your explanations short and to the point."
PROMPT_TEMPLATE = CLAUDE_ROLE + """

Selected text:
{text}

Please provide a clear, simplified explanation of the above text. If it's a single word or short phrase, explain what it means. If it's longer text, simplify and explain it in easy-to-understand terms.
Do not include any question back to the user. Do not include a title. Just provide the markdown formatted short explanation between 100 and 300 characters.
"""
INSIGHT_GENERATION_PROMPT = CLAUDE_ROLE + """
Here is student learning objective for the current study session:
{learning_objective}

Here is the information on student screen:
{text}

Please analyze it and do the following instructions: {instructions}
The output should be in the following format: {output_format}

Important: consider student learning objective when generating insights
"""
SUMMARY_GENERATION_INSTRUCTION = "provide short summary of the screen content"
LINK_GENERATION_INSTRUCTION = "provide web page urls with short descriptions (8 words max offering the student to visit the page) that predict the next step in the learning process based on the screen content. Include links only if you are confident that they are relevant to the student's learning objective."
SUGGESTIONS_GENERATION_INSTRUCTION = "make suggestions how student can continue their learning based on the screen content and your findings"

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

