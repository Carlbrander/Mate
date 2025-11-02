# Configuration file for Context Retrieval Module

# Screenshot capture settings
SCREENSHOT_INTERVAL = 10  # Interval between screenshots in seconds

# API settings
# The API key is loaded from the parent directory's api_key folder
import os
API_KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api_key", "api_key.txt")

# Claude model to use for image analysis
CLAUDE_MODEL = "claude-sonnet-4-5"

# Maximum tokens for API response
MAX_TOKENS = 1500

# Prompt template for image analysis
ANALYSIS_PROMPT = """Analyze the provided screenshot, which contains multiple tabs (e.g., website or app interface). Generate an XML structure that organizes each tab's content, including:

Tab Name: The main content of the tab in a few words

Tab URL: The URL of the tab if available, otherwise leave it blank.

Context: A brief description of the tab's purpose (e.g., "Main dashboard", "Settings page for user preferences").

Text Content: Extract and summarize all visible text in the tab. 

Image Content: Describe key images or visual elements, explaining their role

Return the output in the following XML format:

<Tab>
    <Name>Tab Name</Name>
    <URL>Tab URL</URL>
    <Context>Tab description</Context>
    <TextContent>
        Extracted text content
    </TextContent>
    <ImageContent>
        <Image>
            <Description>Image description</Description>
            <Role>Image role</Role>
        </Image>
    </ImageContent>
</Tab>

Ensure the XML is organized by tab and clearly describes both text and images for each section of the screenshot.
do not include other xml tags than the ones specified.
Be concise and to the point. Dont provide more than 1000 tokens.
Ignore ads and other non-content elements.
Output well formatted xml and nothing else."""

# Storage settings
SAVE_SCREENSHOTS = False  # Whether to save screenshots to disk
SCREENSHOTS_DIR = "context_retrieval/screenshots"  # Directory to save screenshots

# Context output settings
SAVE_CONTEXTS = False  # Whether to save extracted contexts to disk
CONTEXTS_DIR = "context_retrieval/contexts"  # Directory to save context XML files

# Summary history settings
SUMMARY_HISTORY_FILE = "context_retrieval/summary_history.txt"  # File to save learning summary history

# Logging settings
LOG_FILE = "context_retrieval/context_retrieval.log"
LOG_LEVEL = "WARNING"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

