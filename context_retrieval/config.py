# Configuration file for Context Retrieval Module

# Screenshot capture settings
SCREENSHOT_INTERVAL = 50  # Interval between screenshots in seconds

# API settings
# The API key is loaded from the parent directory's api_key folder
import os
API_KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "api_key", "api_key.txt")

# Claude model to use for image analysis
CLAUDE_MODEL = "claude-haiku-4-5"

# Maximum tokens for API response
MAX_TOKENS = 2000

# Prompt template for image analysis
ANALYSIS_PROMPT = """Analyze the provided screenshot, which contains multiple tabs (e.g., website or app interface). Generate an XML structure that organizes each tab's content, including:

Tab Name: The name of the tab (e.g., "Home", "Settings").

Context: A brief description of the tab's purpose (e.g., "Main dashboard", "Settings page for user preferences").

Text Content: Extract and summarize all visible text in the tab, including headings, body text, and buttons, with brief context for each.

Image Content: Describe key images or visual elements, explaining their role (e.g., icons, logos, charts).

Layout (optional): A brief description of the tab's layout (e.g., grid, sidebar).

Return the output in the following XML format:

<Tab>
    <Name>Tab Name</Name>
    <Context>Tab description</Context>
    <TextContent>
        <TextElement>
            <Content>Extracted text</Content>
            <Description>Text purpose or meaning</Description>
        </TextElement>
    </TextContent>
    <ImageContent>
        <Image>
            <Description>Image description</Description>
            <Role>Image role</Role>
        </Image>
    </ImageContent>
    <Layout>
        <LayoutDescription>Layout description</LayoutDescription>
    </Layout>
</Tab>

Ensure the XML is organized by tab and clearly describes both text and images for each section of the screenshot."""

# Storage settings
SAVE_SCREENSHOTS = False  # Whether to save screenshots to disk
SCREENSHOTS_DIR = "context_retrieval/screenshots"  # Directory to save screenshots

# Context output settings
SAVE_CONTEXTS = False  # Whether to save extracted contexts to disk
CONTEXTS_DIR = "context_retrieval/contexts"  # Directory to save context XML files

# Logging settings
LOG_FILE = "context_retrieval/context_retrieval.log"
LOG_LEVEL = "WARNING"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

