from agents import Agent
from agentes.prompts.cooperative_prompt import COOPERATIVE_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

class CooperativeAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Cooperative Agent",
            instructions=COOPERATIVE_PROMPT,
            handoff_description="Agente especialista en dar información sobre cooperativas. Siempre que se hable de cooperativa este agente debe entrar para responder.",
            model=os.getenv("OPEN_AI_MODEL")
        )
