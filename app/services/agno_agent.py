from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools import Toolkit
from datetime import datetime
from agno.utils.log import logger
import re
from difflib import get_close_matches
from pydantic import BaseModel, Field
from sqlmodel import select
from app.database import get_session

from app.models import Contact
from sqlalchemy.sql.operators import ilike_op
import os
from app.config import settings


from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.groq import Groq
import json
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY
class Email(BaseModel):
    recipient_email: str|None = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Body of the email")
    explanation: str = Field(..., description="Explanation of any errors that occurred")


class ContactSearchTool(Toolkit):
    def __init__(self):
      super().__init__(name="contact_search_tool")
      self.register(self.contact_search_tool)
    async def contact_search_tool(self,person_name:str|None):
      """
      Searches for a person's email address in a predefined list of contacts.
      Uses fuzzy matching to handle name variations (e.g., Satya vs Sathya).

      Args:
          person_name (str): The name of the person to search for.

      Returns:
          str: The email address of the person if found, otherwise None.
      """
      if person_name:
        async for session in get_session():
            # First try exact/partial match (case-insensitive)
            result = await session.execute(
                select(Contact).where(ilike_op(Contact.name,f'%{person_name}%'))
            )
            contacts = result.scalars().all()
            
            # If no exact match, try fuzzy matching
            if not contacts or len(contacts) == 0:
                # Get all contacts for fuzzy matching
                all_contacts_result = await session.execute(select(Contact))
                all_contacts = all_contacts_result.scalars().all()
                
                if all_contacts:
                    # Get all names for fuzzy matching (convert to lowercase for comparison)
                    all_names = [c.name for c in all_contacts]
                    all_names_lower = [n.lower() for n in all_names]
                    
                    # Find close matches using lowercase (cutoff=0.6 for good fuzzy matching)
                    # This handles: Satya/sathya/SATHYA, Arjun/aurjun/ARJUN, etc.
                    close_names_lower = get_close_matches(person_name.lower(), all_names_lower, n=1, cutoff=0.6)
                    
                    if close_names_lower:
                        # Find the original name from database
                        matched_index = all_names_lower.index(close_names_lower[0])
                        found_name = all_names[matched_index]
                        contacts = [c for c in all_contacts if c.name == found_name]
                        logger.info(f"Fuzzy matched '{person_name}' to '{found_name}' (case-insensitive)")
            
            contact = contacts[0] if contacts and len(contacts) > 0 else None
            
        logger.info(f"running contact tool for {person_name},")
        if contact:
           logger.info(f"contact :{contact.email}")
        if isinstance(contact,Contact):
          return f"the very important contact result **recipient_email** at contact search is {contact.email}"
        else:
          return "No contact found with that name."
      else:
         return "No contact found with that name"


class TimeTool(Toolkit):
    def __init__(self):
        super().__init__(name="time_tool")
        self.register(self.get_current_time)
    
    def get_current_time(self) -> str:
        """
        Returns the current date and time in IST (Indian Standard Time).
        Use this to get accurate current date/time for calculating dates like 'tomorrow', 'next week', etc.
        
        Returns:
            str: Current date and time in IST format 'YYYY-MM-DD HH:MM:SS IST'
        """
        from datetime import datetime, timezone, timedelta
        
        # IST is UTC+5:30
        ist_offset = timezone(timedelta(hours=5, minutes=30))
        ist_time = datetime.now(ist_offset)
        
        return ist_time.strftime("%Y-%m-%d %H:%M:%S IST")
        

def create_parser_agent(user_session_id:str):
   # Setup database for session storage and memory
   db = SqliteDb(db_file=settings.CHATBASE_URL)
   
   email_parer_agent = Agent(
    model=Groq(id=settings.GROQ_MODEL_NAME),
    tools=[ContactSearchTool(), TimeTool()],
    user_id = user_session_id,
    session_id = user_session_id,
    db=db,
    enable_user_memories=False,  # Re-enabled with better instructions
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_messages=3,
    role ="Email Parser",
    description="You are a helpful assistant. your job is to construct the email body from a voice transcription by looking carefully extracting recipient email,subject,body,and recipient name",
    instructions="""
   
    IMPORTANT GUIDELINES:
    0. You have access to tools: contact_search_tool and time_tool. Always use time_tool to get current date/time before calculating dates.
    
    DATE AND TIME HANDLING:
    1. ALWAYS use time_tool first to get the current date and time as reference.
    2. When the text mentions relative times (today, tomorrow, next week, etc), calculate the exact date based on time_tool output.
    3. Format dates as dd/mm/yyyy in the email body.
    4. Remove all relative timing phrases like "tomorrow", "next week" - replace with actual dates.
    
    NAME HANDLING - CRITICAL:
    5. When searching for a contact, use the EXACT name mentioned in the transcription.
    6. If contact_search_tool returns a name that's slightly different (e.g., you searched "Satya" but found "Sathya"), 
       USE THE FOUND NAME from the tool result, NOT the transcription.
    7. Example: Transcription says "Satya" → Tool finds "Sathya" → Use "Sathya" in recipient_name field.
    
    EMAIL CONSTRUCTION:
    8. Extract the recipient's name from the input text.
    9. Use contact_search_tool to find the recipient's email address. If found, use it. Otherwise set to null.
    10. Extract or generate an appropriate subject line.
    11. Construct the email body based on the input text.
    12. If there are additional instructions for email formatting in the text, apply them to the body.
    
    RECIPIENT EMAIL PRIORITY:
    13. First priority: **recipient_mail_from_transcription** if explicitly mentioned in voice
    14. Second priority: **recipient_email_from_search** from contact_search_tool
    15. Last option: null if neither available

    OUTPUT FORMAT:
    Return valid JSON with this structure:
    {
        "recipient_name": [exact name from contact tool if found, or from transcription],
        "recipient_email": [email address or null],
        "subject": [subject line or null],
        "body": [email body with actual dates, not relative terms],
        "explanation": [any errors or notes]
    }
    """,
    
    

    
   )
   
   return email_parer_agent

email_finish_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    role ="Email Finisher",
    description="You are a helpful assistant. your job is to construct the email body from a textual description by looking carefully extracting recipient email,subject,body,and recipient name.",
    instructions=""" 
    1. Always use the current date time  as reference, if the text contains time related words like last week,today,yesterday,day after tomorrow, year later etc,prefer mentioning date in   dd/mm/yyyy format in given in the user input.remove relative timings from message body
    2. Extract the recipient's name from the input text.
    3. Extract the subject of the email from the input text.
    4. Construct and rephrase the email body based on the input text professionally,add spaces and newlines if necessary add best regards using sender's name with proper and professional ending.
    5. Return the output in JSON format with the following structure:
    
    {
        "recipient_name": [recipient_name or null],
        "recipient_email": [recipient_email or null],
        "subject": [subject or null],
        "body": [email body],
        "explanation": [anything error occurs]
    }
    """,
    output_schema=Email
    )
   

async def generate_email(transcribed_text:str,recipient_name=None,recipient_email=None,user_session_id:str="default"):
        email_parser_agent = create_parser_agent(user_session_id)
        agent1_message_coroutine =await email_parser_agent.arun(transcribed_text+f'todays date and time  is {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")} + the **recipient_mail_from_transcription** is {recipient_email}, the recipient_name is {recipient_name}')
        agent1_message = agent1_message_coroutine.messages[-1].content
        logger.info(f"constructed_base{agent1_message}")
        agent2_message = email_finish_agent.run(agent1_message).messages[-1].content
        logger.info(f"constructed_finisher {agent2_message}")
        return agent2_message