import json
import os
import sys

from dataclasses import dataclass

from anthropic import Anthropic

# Add parent directory to path to import main config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


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
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    max_retries = 3
    for attempt in range(max_retries):
        print(f"Generating links... Attempt {attempt + 1} of {max_retries}")
        response = client.messages.create(
        model=config.CLAUDE_MODEL,
        messages=[
            {
                "role": "user", 
                "content": config.INSIGHT_GENERATION_PROMPT.format(
                    learning_objective=learning_objective,
                    text=context,
                    instructions=config.LINK_GENERATION_INSTRUCTION,
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
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    max_retries = 3
    for attempt in range(max_retries):
        print(f"Generating insights... Attempt {attempt + 1} of {max_retries}")
        response = client.messages.create(
            model=config.CLAUDE_MODEL,
            messages=[
                {
                    "role": "user", 
                    "content": config.INSIGHT_GENERATION_PROMPT.format(
                        learning_objective=learning_objective,
                        text=context,
                        instructions="; ".join([config.SUMMARY_GENERATION_INSTRUCTION, config.LINK_GENERATION_INSTRUCTION, config.SUGGESTIONS_GENERATION_INSTRUCTION]),
                        output_format='{"summary": "...", "links": [{"url": "https://link1.com", "summary": "summary1"}, {"url": "https://link2.com", "summary": "summary2"}, ...], "suggestions": "..."}',
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