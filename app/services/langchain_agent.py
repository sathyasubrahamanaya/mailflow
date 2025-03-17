from langchain.agents import initialize_agent, Tool, AgentType
from langchain_groq import ChatGroq  # Updated import from langchain-groq
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from duckduckgo_search import DDGS
from sqlalchemy.future import select
from app.database import get_session
from app.models import User, Contact
from app.services.email_prompt import prompt
import datetime

class EmailGenerationAgent:
    def __init__(self):
        from app.config import settings
        self.llm = ChatGroq(model=settings.GROQ_MODEL_NAME,api_key=settings.GROQ_API_KEY)
        
        self.prompt_template = PromptTemplate(
            input_variables=["transcribed_text","recipient_email"],
            template=prompt
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
    def time_now(self):
        return datetime.datetime.now()
    
    def generate_email(self, transcribed_text: str, recipient_name: str=None, recipient_email: str=None):
        return self.llm_chain.invoke({
            "transcribed_text": transcribed_text,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email
        })
