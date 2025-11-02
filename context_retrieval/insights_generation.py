import json
import os
import sys
from datetime import datetime

from dataclasses import dataclass

from anthropic import Anthropic

# Add parent directory to path to import main config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config as main_config

# Summary history file path (defined here to avoid import issues)
SUMMARY_HISTORY_FILE = "context_retrieval/summary_history.txt"


@dataclass
class Link:
    summary: str | None = None
    url: str | None = None


@dataclass
class Insights:
    summary: str | None = None
    links: list[Link] | None = None
    suggestions: str | None = None

def generate_links(learning_objective: str, context: str) -> list[str] | None:
    client = Anthropic(api_key=main_config.ANTHROPIC_API_KEY)
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Generating links... Attempt {attempt + 1} of {max_retries}")
        response = client.messages.create(
        model=main_config.CLAUDE_MODEL,
        messages=[
            {
                "role": "user", 
                "content": main_config.INSIGHT_GENERATION_PROMPT.format(
                    learning_objective=learning_objective,
                    text=context,
                    instructions=main_config.LINK_GENERATION_INSTRUCTION,
                    output_format='{"links": [{"url": "link1", "summary": "summary1"}, {"url": "link2", "summary": "summary2"}, ...]}',
                ),
            }
        ],
            max_tokens=1000,
        )
        # Check if the assistant's message content is not None, break if it's valid
        if response.content and response.content[0].text:
            break
        print(f"Error: {response.content[0].text}")
    
    # Get the assistant's message content (assume only one message and one content block)
    raw_output = response.content[0].text if response.content else None
    raw_output = raw_output.removeprefix("```json\n").removesuffix("\n```")
    if raw_output is None:
        return None
    try:
        data = json.loads(raw_output)
        # Convert link dictionaries to Link objects
        if 'links' in data and isinstance(data['links'], list):
            data['links'] = [Link(**link) if isinstance(link, dict) else link for link in data['links']]
        return Insights(**data)
    except (json.JSONDecodeError, TypeError):
        return None

def generate_insights(learning_objective: str, context: str) -> Insights | None:
    client = Anthropic(api_key=main_config.ANTHROPIC_API_KEY)

    max_retries = 3
    for attempt in range(max_retries):
        print(f"Generating insights... Attempt {attempt + 1} of {max_retries}")
        response = client.messages.create(
            model=main_config.CLAUDE_MODEL,
            messages=[
                {
                    "role": "user", 
                    "content": main_config.INSIGHT_GENERATION_PROMPT.format(
                        learning_objective=learning_objective,
                        text=context,
                        instructions="; ".join([main_config.SUMMARY_GENERATION_INSTRUCTION, main_config.LINK_GENERATION_INSTRUCTION, main_config.SUGGESTIONS_GENERATION_INSTRUCTION]),
                        output_format='{"summary": "...", "links": [{"url": "link1", "summary": "summary1"}, {"url": "link2", "summary": "summary2"}, ...], "suggestions": "..."}',
                    ),
                }
            ],
            max_tokens=1000,
        )
        # Check if the assistant's message content is not None, break if it's valid
        if response.content and response.content[0].text:
            break
        print(f"Error: {response.content[0].text}")
    
    # Get the assistant's message content (assume only one message and one content block)
    raw_output = response.content[0].text if response.content else None
    raw_output = raw_output.removeprefix("```json\n").removesuffix("\n```")
    if raw_output is None:
        return None
    try:
        data = json.loads(raw_output)
        # Convert link dictionaries to Link objects
        if 'links' in data and isinstance(data['links'], list):
            data['links'] = [Link(**link) if isinstance(link, dict) else link for link in data['links']]
        return Insights(**data)
    except (json.JSONDecodeError, TypeError):
        return None


# Summary history management
def load_summary_history() -> str:
    """
    Load the existing summary history from file.
    
    Returns:
        The existing summary history, or empty string if file doesn't exist
    """
    if not os.path.exists(SUMMARY_HISTORY_FILE):
        return ""
    
    try:
        with open(SUMMARY_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error loading summary history: {e}")
        return ""


def save_summary_history(summary: str):
    """
    Save the updated summary history to file.
    
    Args:
        summary: The updated summary to save
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(SUMMARY_HISTORY_FILE), exist_ok=True)
    
    try:
        with open(SUMMARY_HISTORY_FILE, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary history saved to: {SUMMARY_HISTORY_FILE}")
    except Exception as e:
        print(f"Error saving summary history: {e}")


def flush_summary_history():
    """
    Flush/clear the summary history (start a new session).
    """
    try:
        if os.path.exists(SUMMARY_HISTORY_FILE):
            os.remove(SUMMARY_HISTORY_FILE)
            print("Summary history flushed for new session")
        return True
    except Exception as e:
        print(f"Error flushing summary history: {e}")
        return False


def update_summary_history(learning_objective: str, new_context: str) -> str | None:
    """
    Update the summary history with new context from screenshot analysis.
    This function reads the existing summary, analyzes the new context,
    and updates the summary if relevant changes happened.
    
    Args:
        learning_objective: The student's learning objective for the session
        new_context: The new context extracted from the latest screenshot (XML format)
    
    Returns:
        The updated summary, or None if update failed
    """
    client = Anthropic(api_key=main_config.ANTHROPIC_API_KEY)
    
    # Load existing summary
    existing_summary = load_summary_history()
    
    # Build the prompt for updating the summary
    if existing_summary:
        prompt = f"""You are helping a student track their learning progress. 

Student's Learning Objective:
{learning_objective}

Previous Summary of Research/Learning Activities:
{existing_summary}

New Screen Content (from latest screenshot):
{new_context}

Task: Analyze the new screen content and determine if it represents relevant changes or progress in the student's learning journey. If there are relevant changes (new topics explored, different resources visited, progress made, etc.), update the summary to include this new information. If the content is essentially the same or not relevant, keep the existing summary unchanged.

The updated summary should:
1. Be chronological - capture the progression of learning activities
2. Be concise but informative - highlight key topics, resources, and activities
3. Focus on the learning journey - what has been studied, explored, or researched
4. Include timestamps or time references where appropriate
5. Grow over time as new relevant activities are detected

Output ONLY the updated summary text (no extra formatting, no explanations, no titles). If no relevant changes detected, output the existing summary unchanged."""
    else:
        prompt = f"""You are helping a student track their learning progress. 

Student's Learning Objective:
{learning_objective}

Screen Content (from first screenshot):
{new_context}

Task: Create the initial summary of the student's learning activities based on the screen content. This is the beginning of tracking their learning journey.

The summary should:
1. Be concise but informative - highlight key topics, resources, and activities
2. Focus on what the student is currently studying or researching
3. Include a timestamp reference for this first entry

Output ONLY the summary text (no extra formatting, no explanations, no titles)."""
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Updating summary history... Attempt {attempt + 1} of {max_retries}")
        try:
            response = client.messages.create(
                model=main_config.CLAUDE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
            )
            
            # Get the updated summary
            if response.content and response.content[0].text:
                updated_summary = response.content[0].text.strip()
                
                # Add timestamp to the update
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if not existing_summary:
                    # First entry
                    updated_summary = f"[Session Started: {timestamp}]\n\n{updated_summary}"
                
                # Save the updated summary
                save_summary_history(updated_summary)
                
                return updated_summary
            else:
                print(f"Error: No content in response")
        except Exception as e:
            print(f"Error in attempt {attempt + 1}: {e}")
    
    return None


def get_current_summary() -> str:
    """
    Get the current summary history.
    
    Returns:
        The current summary history, or empty string if none exists
    """
    return load_summary_history()


def generate_final_summary(learning_objective: str) -> str | None:
    """
    Generate a nicely formatted markdown summary of the entire learning session.
    This is called when the user presses the + button to get a final summary.
    
    Args:
        learning_objective: The student's learning objective for the session
    
    Returns:
        Formatted markdown summary, or None if generation failed
    """
    client = Anthropic(api_key=main_config.ANTHROPIC_API_KEY)
    
    # Load the raw summary history
    raw_summary = load_summary_history()
    
    if not raw_summary:
        return "# Learning Session Summary\n\nNo learning activity detected in this session yet."
    
    prompt = f"""You are creating a final learning session summary for a student.

Student's Learning Objective:
{learning_objective}

Raw Session History:
{raw_summary}

Task: Transform this raw history into a beautiful, well-formatted markdown summary that the student can read to understand their progress. Include:

1. **Session Overview** - When it started, main topics covered
2. **Key Topics Explored** - List the main subjects/areas studied
3. **Facts & Concepts Learned** - Important facts, concepts, or information discovered (only relevant to the learning objective)
4. **Resources Used** - Websites, articles, or tools visited
5. **Progress Made** - What was accomplished during the session

Make it inspiring and encouraging. Use proper markdown formatting:
- Use # for title, ## for sections
- Use **bold** for emphasis
- Use bullet points (-) for lists
- Keep it concise but informative
- Focus only on relevant facts related to the learning objective

Output ONLY the markdown text."""
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Generating final summary... Attempt {attempt + 1} of {max_retries}")
        try:
            response = client.messages.create(
                model=main_config.CLAUDE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
            )
            
            if response.content and response.content[0].text:
                return response.content[0].text.strip()
            else:
                print(f"Error: No content in response")
        except Exception as e:
            print(f"Error in attempt {attempt + 1}: {e}")
    
    return None