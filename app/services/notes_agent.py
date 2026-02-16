from agno.agent import Agent
from agno.models.groq import Groq

from datetime import datetime
from app.config import settings
from app.services.agno_agent import TimeTool

# Configure the Agent to return a STRING
note_maker_agent = Agent(
    model=Groq(id=settings.GROQ_MODEL_NAME), 
    role="Professional Note Taker",
    description="You are an expert at organizing messy thoughts into clean, readable markdown notes.",
    tools=[TimeTool()],
    # markdown=True ensures the internal system prompt encourages markdown formatting
    markdown=True, 
    instructions="""
    You will receive a Voice Transcription and optional User Text.
    
    YOUR GOAL:
    Merge them into a single, professional note in Markdown format.
    
    FORMATTING RULES:
    1. Start with a **# Title** (H1).
    2. Follow with the **refined content**. Fix grammar, remove filler words ("um", "uh"), and improve flow.
    3. Use **bullet points** or **numbered lists** where appropriate.
    4. Resolve relative dates (like "tomorrow") using the `time_tool`.
    5. If there are tasks, add a section: **## Action Items**.
    6. End with a line of **Tags:** (e.g., #Meeting #Ideas).
    
    Do not output JSON. Output the final Note text directly.
    """
)

async def generate_smart_note(transcribed_text: str, user_text: str | None = None) -> str:
    """
    Returns a formatted Markdown string.
    """
    input_prompt = f"**Voice Transcription:**\n{transcribed_text}\n"
    
    if user_text:
        input_prompt += f"\n**User Context:**\n{user_text}"
    
    input_prompt += f"\n\n(Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"

    # Run agent and get the string content
    response = await note_maker_agent.arun(input_prompt) # type: ignore
    
    # Ensure we return a string (response.content is usually the string)
    return str(response.content)