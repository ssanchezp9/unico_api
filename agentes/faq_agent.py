from agents import Agent
from agentes.prompts.faq_prompt import FAQ_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

class FAQAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Frequent Questions Agent",
            instructions=FAQ_PROMPT,
            handoff_description="Agente especialista en responder a preguntas que tengan los usuarios. Siempre que se haga una pregunta este agente debe ser el primero en ser consultado.",
            model=os.getenv("OPEN_AI_MODEL")
        )
