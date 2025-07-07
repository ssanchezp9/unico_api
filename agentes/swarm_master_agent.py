from agents import Agent
from agentes.google_calendar_agent import GoogleCalendarAgent
from agentes.proyectos_agent import ProyectosAgent
from agentes.faq_agent import FAQAgent
from agentes.cooperative_agent import CooperativeAgent
from agentes.prompts.swar_master_prompt import UNICOS_HOMES_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

class SwarmMasterAgent(Agent):
    def __init__(self):
        """Asistente virtual oficial de ÚNICO Homes"""
        google_calendar_agent = GoogleCalendarAgent()
        proyectos_agent = ProyectosAgent()
        faq_agent = FAQAgent()
        cooperative_agent = CooperativeAgent()

        super().__init__(
            name="Asistente Virtual ÚNICO Homes",
            handoff_description="Asistente especializado en servicios inmobiliarios de ÚNICO Homes - gestión integral de proyectos, cooperativas, promociones y asesoramiento.",
            instructions=UNICOS_HOMES_PROMPT,
            model=os.getenv("OPEN_AI_MODEL"),
            handoffs=[
                google_calendar_agent, 
                proyectos_agent,
                faq_agent,
                cooperative_agent
            ],
        )