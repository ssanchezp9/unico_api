from agents import Agent
from tools.proyectos import (
    get_future_promotions, 
    get_current_promotions, 
    get_past_promotions, 
    get_information_for_specific_promotion_url
)
from agentes.prompts.proyectos_prompt import PROYECTOS_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

class ProyectosAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Proyectos Agent",
            instructions=PROYECTOS_PROMPT,
            handoff_description="Agente especialista en dar información sobre proyectos futuros, proyectos en comercialización y proyectos vendidos. Puede acceder también a la información de una promoción específica a través de su URL.",
            model=os.getenv("OPEN_AI_MODEL"),
            tools=[
                get_future_promotions,
                get_current_promotions,
                get_past_promotions,
                get_information_for_specific_promotion_url
            ]
        )
        