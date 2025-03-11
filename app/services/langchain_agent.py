from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq  # Updated import from langchain-groq
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from duckduckgo_search import DDGS
from sqlalchemy.future import select
from app.database import get_session
from app.models import User, Contact

class EmailGenerationAgent:
    def __init__(self):
        from app.config import settings
        self.llm = ChatGroq(model=settings.GROQ_MODEL_NAME)
        
        self.prompt_template = PromptTemplate(
         input_variables=["transcribed_text", "recipient_name", "recipient_email"],
         template="""
          Using the transcribed text as the main message, generate a professional email addressed to {recipient_name} at {recipient_email} in the following Gmail format:

          Subject: [A concise subject line reflecting the purpose of the transcribed text]

          Dear [Recipient Name],

          [A polite and professional rephrasing of the transcribed text: "{transcribed_text}"]

          Best regards,
          [Your Name]

          The output must include only the email content as shown above—subject line, greeting, body, and closing—with no additional text, commentary, or explanations. Rephrase the transcribed text "{transcribed_text}" into a concise, polite, and professional body suitable for an email.
       """
      )
        
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        
        self.tools = [
            Tool(
                name="ContactSearch",
                func=self.contact_search,
                description="Search user's contacts by name"
            ),
            Tool(
                name="WebSearch",
                func=self.web_search,
                description="Search the internet using DuckDuckGo"
            )
        ]
        
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
    
    async def contact_search(self, query: str, user_id: int):
        async for session in get_session():
            result = await session.execute(
                select(Contact).where(
                    Contact.user_id == user_id,
                    Contact.name.contains(query) | Contact.email.contains(query)
                )
            )
            return result.scalars().all()
    
    def web_search(self, query: str):
        results = DDGS(query, max_results=10, region="in-en", timelimit='d')
        return results
    
    def generate_email(self, transcribed_text: str, recipient_name: str, recipient_email: str):
        return self.llm_chain.run({
            "transcribed_text": transcribed_text,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email
        })
