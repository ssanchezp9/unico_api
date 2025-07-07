from agents import Agent
from tools.google_calendar import (
    crear_videollamada_promocion,
    ver_citas_dia_especifico,
    obtener_fecha_actual,
    mostrar_slots_libres,
)
from agentes.prompts.google_calendar_prompt import GOOGLE_CALENDAR_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

class GoogleCalendarAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Asistente de Reuniones",
            instructions=GOOGLE_CALENDAR_PROMPT,
            handoff_description="Asistente especializado en programar videollamadas promocionales respetando horarios laborales y privacidad de citas.",
            model=os.getenv("OPEN_AI_MODEL"),
            tools=[
                crear_videollamada_promocion,
                ver_citas_dia_especifico,
                obtener_fecha_actual,
                mostrar_slots_libres,
            ]
        )
