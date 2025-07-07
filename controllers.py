from fastapi import APIRouter, Body
from pydantic import BaseModel
from utils.conversation_manager import ConversationManager
from agentes.swarm_master_agent import SwarmMasterAgent
from agents import Runner
import uuid

router = APIRouter()
conversation_manager = ConversationManager()

class Message(BaseModel):
    user_input: str

async def call_agent(user_input: str, conversation_id: str):
    swarm_master_agent = SwarmMasterAgent()

    conversation_manager.add_message(conversation_id, "user", user_input)
    
    historial_conversacion = conversation_manager.get_history(conversation_id)

    result = await Runner.run(
        swarm_master_agent,
        input=historial_conversacion
    )

    # Agregar la respuesta del agente al historial
    conversation_manager.add_message(conversation_id, "assistant", result.final_output)

    return result.final_output

@router.post("/conversation")
async def start_conversation(message: Message):
    conversation_id = str(uuid.uuid4())
    response = await call_agent(message.user_input, conversation_id)
    return {"conversation_id": conversation_id, "response": response}

@router.post("/conversation/{conversation_id}")
async def chat(conversation_id: str, message: Message):
    response = await call_agent(message.user_input, conversation_id)
    return {"response": response}
