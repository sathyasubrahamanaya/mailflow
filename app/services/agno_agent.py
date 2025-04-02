from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools import Toolkit
from datetime import datetime
from agno.utils.log import logger
import re
from pydantic import BaseModel, Field
from sqlmodel import select
from app.database import get_session

from app.models import Contact
from sqlalchemy.sql.operators import ilike_op
import os
from app.config import settings


from agno.agent import Agent, AgentMemory
from agno.memory.db.sqlite import SqliteMemoryDb
from agno.models.groq import Groq

from agno.storage.agent.sqlite import SqliteAgentStorage
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

      Args:
          person_name (str): The name of the person to search for.

      Returns:
          str: The email address of the person if found, otherwise None.
      """
      if person_name:
        async for session in get_session():
            result = await session.execute(
                select(Contact).where(ilike_op(Contact.name,f'%{person_name}%'))
            )
            contact = result.scalars().all()
            if isinstance(contact,list):
               contact = contact[0]
        logger.info(f"running contact tool for {person_name},")
        if contact:
           logger.info(f"contact :{contact.email}")
        if isinstance(contact,Contact):
          return f"the very important contact result **recipient_email** at contact search is {contact.email}"
        else:
          return "No contact found with that name."
      else:
         return "No contact found with that name"
        

def create_parser_agent(user_session_id:str):
   email_parer_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[ContactSearchTool()],
    user_id = user_session_id,
    session_id = user_session_id,
    memory=AgentMemory(db=SqliteMemoryDb(db_file=settings.CHATBASE_URL,table_name="agent_memory")),

    storage=SqliteAgentStorage(table_name="agent_sessions", db_file=settings.CHATBASE_URL),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=3,
    role ="Email Parser",
    description="You are a helpful assistant. your job is to construct the email body from a voice transcription by looking carefully extracting recipient email,subject,body,and recipient name",
    instructions="""
   
    0. You have access to tools:contact_search_tool.always note down the date mentioned, look out for chat history for more context
    1. Always use the current date time  as reference, if the text contains time related words like last week,today,yesterday,day after tomorrow, year later etc,prefer mentioning date in   dd/mm/yyyy format in given in the user input.remove relative timings from message body
    2. Extract the recipient's name from the input text.
    3. Use the contact_search_tool to find the recipient's email address based on the extracted name if given. Otherwise set it to null.
    4. Extract the subject of the email from the input text.
  5. Construct the email body based on the input text.
  5a. after constructing body look for any addtional instruction given in the text for email formulation if yes then modify email body according to it
  5b. if subject is not given make a appropriate subject else use the given subject or None
  5c.In a given voice transcript **recipient_mail_from_transcription** address or recipient email may be given at the end of voice transcription or not. 
    later when you are using contact_search_tool you may get **recipient_email_from_search** or not.
    so first prefer that  **recipient_mail_from_transcription** if it is not None/Null else if you should use **recipient_email_from_search** or as last option you can use null

    6. Return the output in JSON format with the following structure:
    {
        "recipient_name": [recipient_name or null],
        "recipient_email": [recipient_email or null],
        "subject": [subject or null],
        "body": [email body],
        "explanation": [anything error occurs]
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
    response_model = Email,
    structured_outputs=True
    )
   

async def generate_email(transcribed_text:str,recipient_name=None,recipient_email=None,user_session_id:str="default"):
        email_parser_agent = create_parser_agent(user_session_id)
        agent1_message_coroutine =await email_parser_agent.arun(transcribed_text+f'todays date and time  is {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")} + the **recipient_mail_from_transcription** is {recipient_email}, the recipient_name is {recipient_name}')
        agent1_message = agent1_message_coroutine.messages[-1].content
        logger.info(f"constructed_base{agent1_message}")
        agent2_message = email_finish_agent.run(agent1_message).messages[-1].content
        logger.info(f"constructed_finisher {agent2_message}")
        return agent2_message