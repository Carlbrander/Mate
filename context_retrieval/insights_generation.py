import json
import os
import sys
import re

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

# Read visited URLs from environment variable (comma-separated)
visited_urls_env = os.getenv('VISITED_URLS', '')
visited_urls = set(url.strip() for url in visited_urls_env.split(',') if url.strip()) if visited_urls_env else set()

def _add_visited_url(url: str | None) -> None:
    """Add a URL to visited_urls set and update the VISITED_URLS environment variable."""
    if url:
        visited_urls.add(url)
        # Update environment variable with comma-separated URLs
        os.environ['VISITED_URLS'] = ', '.join(sorted(visited_urls))

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
                    instructions=config.LINK_GENERATION_INSTRUCTION.format(visited_urls=", ".join(visited_urls) if visited_urls else "none"),
                    output_format='{"links": [{"url": "https://link.com", "summary": "link summary"}]}',
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
    raw_output = re.sub(r'\n```\n*$', '', re.sub(r'^```json\n', '', raw_output))
    if raw_output is None:
        return None
    try:
        data = json.loads(raw_output)
        # Convert link dictionaries to Link objects
        if 'links' in data and isinstance(data['links'], list):
            data['links'] = [Link(**link) if isinstance(link, dict) else link for link in data['links']]
        _add_visited_url(data['links'][0].url if data['links'] else None)
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
                        instructions="; ".join([config.SUMMARY_GENERATION_INSTRUCTION, config.LINK_GENERATION_INSTRUCTION.format(visited_urls=", ".join(visited_urls)), config.SUGGESTIONS_GENERATION_INSTRUCTION]),
                        output_format='{"summary": "...", "links": [{"url": "https://link.com", "summary": "link summary"}], "suggestions": "..."}',
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
    raw_output = re.sub(r'\n```\n*$', '', re.sub(r'^```json\n', '', raw_output))
    if raw_output is None:
        return None
    try:
        data = json.loads(raw_output)
        # Convert link dictionaries to Link objects
        if 'links' in data and isinstance(data['links'], list):
            data['links'] = [Link(**link) if isinstance(link, dict) else link for link in data['links']]
        _add_visited_url(data['links'][0].url if data['links'] else None)
        return Insights(**data)
    except (json.JSONDecodeError, TypeError):
        return None