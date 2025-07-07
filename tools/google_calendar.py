import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from agents import function_tool
import os


# Configuración inicial de la API de Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]
_calendar_service = None

def _init_service(credentials_file="credentials.json"):
    global _calendar_service
    if _calendar_service is None:
        creds = None
        
        # Prioridad 1: Usar la variable de entorno en producción (Railway)
        token_json_content = os.getenv("GOOGLE_TOKEN_JSON")
        if token_json_content:
            # Si la variable existe, la escribimos en un archivo token.json para que el resto del código la use
            with open("token.json", "w") as token_file:
                token_file.write(token_json_content)

        # Prioridad 2: Usar el archivo local token.json (para desarrollo)
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # Si no hay credenciales válidas, intentar refrescar o crear nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Este bloque solo se ejecutará en local si no existe token.json
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Guardar las credenciales actualizadas o nuevas en el archivo token.json
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        _calendar_service = build("calendar", "v3", credentials=creds)
    return _calendar_service

@function_tool
def ver_citas_futuras(max_results: int = 10, days_ahead: int = 7) -> str:
    """Consulta las próximas citas programadas en el calendario."""
    service = _init_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)).isoformat() + "Z"
    try:
        events = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])
        if not events:
            return "No hay citas programadas en los próximos días."
        
        citas_info = []
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '(sin título)')
            attendees = event.get('attendees', [])
            
            # Formatear fecha y hora
            if 'T' in start_time:
                dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                fecha_hora = dt.strftime("%d/%m/%Y a las %H:%M")
            else:
                fecha_hora = start_time
            
            participantes = ", ".join([att.get('email', '') for att in attendees if att.get('email')])
            if participantes:
                citas_info.append(f"📅 {fecha_hora} - {summary}\n   👥 Participantes: {participantes}")
            else:
                citas_info.append(f"📅 {fecha_hora} - {summary}")
        
        return "\n\n".join(citas_info)
    except HttpError as err:
        return f"Error al consultar citas: {err}"

@function_tool
def crear_videollamada_promocion(
    dia: str,  # formato: "2025-07-15"
    hora: str,  # formato: "14:30"
    promocion: str,  # nombre de la promoción consultada
    email: str,  # correo del interesado
    telefono: str,  # teléfono del interesado
    nombre: str  # nombre del interesado
) -> str:
    """Crea una videollamada de 30 minutos para presentar una promoción específica."""
    service = _init_service()
    
    # Construir fecha y hora de inicio
    try:
        start_dt = datetime.datetime.strptime(f"{dia} {hora}", "%Y-%m-%d %H:%M")
        end_dt = start_dt + datetime.timedelta(minutes=30)  # Duración fija de 30 minutos
    except ValueError:
        return "❌ Error: Formato de fecha u hora incorrecto. Use YYYY-MM-DD para la fecha y HH:MM para la hora."
    
    # Verificar horario laboral
    hora_inicio = start_dt.time()
    hora_fin = end_dt.time()
    
    # Horarios permitidos: 09:00-14:00 y 15:00-19:00
    turno_manana_inicio = datetime.time(9, 0)
    turno_manana_fin = datetime.time(14, 0)
    turno_tarde_inicio = datetime.time(15, 0)
    turno_tarde_fin = datetime.time(19, 0)
    
    # Verificar que la cita esté dentro del horario laboral
    en_turno_manana = turno_manana_inicio <= hora_inicio < turno_manana_fin and turno_manana_inicio < hora_fin <= turno_manana_fin
    en_turno_tarde = turno_tarde_inicio <= hora_inicio < turno_tarde_fin and turno_tarde_inicio < hora_fin <= turno_tarde_fin
    
    if not (en_turno_manana or en_turno_tarde):
        return f"""❌ Lo siento, no puedo programar citas fuera del horario laboral.
        
🕒 Horarios disponibles:
• Mañanas: 09:00 - 14:00
• Tardes: 15:00 - 19:00

💡 Por favor, elija una hora dentro de estos rangos. Recuerde que las reuniones duran 30 minutos."""
    
    # Verificar conflictos con citas existentes
    time_min = start_dt.isoformat() + "Z"
    time_max = end_dt.isoformat() + "Z"
    
    try:
        # Buscar eventos que se solapen con la hora solicitada
        existing_events = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True
        ).execute().get("items", [])
        
        if existing_events:
            # Sugerir horarios alternativos sin revelar información de otras citas
            return f"""❌ Lo siento, no está disponible a las {hora} del {start_dt.strftime('%d/%m/%Y')}.

💡 ¿Le gustaría que le sugiera otros horarios disponibles para ese día?"""
            
    except HttpError as err:
        return f"❌ Error al verificar disponibilidad: {err}"
    
    start_datetime = start_dt.isoformat()
    end_datetime = end_dt.isoformat()
    
    # Crear descripción personalizada
    description = f"""
🎯 Reunión de presentación de promoción: {promocion}

👤 Participante: {nombre}
📧 Email: {email}
📞 Teléfono: {telefono}

📝 Información adicional:
{nombre} ha solicitado una cita para conocer más detalles sobre la promoción "{promocion}".

💡 Mientras tanto, puede visitar nuestra página web para obtener más información sobre nuestros servicios y promociones disponibles.

⏰ Duración: 30 minutos
🔗 La videollamada se realizará a través de Google Meet (enlace automático)
"""
    
    # Crear evento con Google Meet automático
    body = {
        "summary": f"Presentación promoción: {promocion} - {nombre}",
        "location": "Videollamada Google Meet",
        "description": description,
        "start": {"dateTime": start_datetime, "timeZone": "Europe/Madrid"},
        "end": {"dateTime": end_datetime, "timeZone": "Europe/Madrid"},
        "attendees": [{"email": email}],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{start_dt.strftime('%Y%m%d%H%M')}-{hash(email) % 10000}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        },
        "reminders": {
            "useDefault": False, 
            "overrides": [
                {"method": "email", "minutes": 60},  # Recordatorio 1 hora antes
                {"method": "popup", "minutes": 15},  # Recordatorio 15 minutos antes
            ]
        },
    }
    
    try:
        created = service.events().insert(
            calendarId="primary", 
            body=body, 
            conferenceDataVersion=1  # Necesario para crear Google Meet
        ).execute()
        
        meet_link = created.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', 'No disponible')
        event_link = created.get('htmlLink', 'No disponible')
        
        return f"""✅ Videollamada creada exitosamente

📅 Fecha y hora: {start_dt.strftime('%d/%m/%Y a las %H:%M')}
👤 Participante: {nombre} ({email})
🎯 Promoción: {promocion}
🔗 Enlace Google Meet: {meet_link}
📋 Ver evento: {event_link}

✉️ Se ha enviado automáticamente la invitación al correo {email}"""
        
    except HttpError as err:
        return f"❌ Error al crear la videollamada: {err}"

@function_tool
def ver_citas_dia_especifico(fecha: str) -> str:
    """Consulta las citas programadas para un día específico. Formato de fecha: YYYY-MM-DD"""
    service = _init_service()
    
    try:
        # Parsear la fecha proporcionada
        target_date = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        time_min = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
        time_max = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"
    except ValueError:
        return "Error: Formato de fecha incorrecto. Use el formato YYYY-MM-DD (ej: 2025-07-15)"
    
    try:
        events = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])
        
        if not events:
            fecha_formateada = target_date.strftime("%d/%m/%Y")
            return f"No hay citas programadas para el {fecha_formateada}."
        
        fecha_formateada = target_date.strftime("%d/%m/%Y")
        citas_info = [f"📅 Agenda del {fecha_formateada}:\n"]
        
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', '(sin título)')
            attendees = event.get('attendees', [])
            
            # Formatear hora
            if 'T' in start_time:
                dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                hora = dt.strftime("%H:%M")
            else:
                hora = "Todo el día"
            
            participantes = ", ".join([att.get('email', '') for att in attendees if att.get('email')])
            if participantes:
                citas_info.append(f"🕒 {hora} - {summary}\n   👥 Participantes: {participantes}")
            else:
                citas_info.append(f"🕒 {hora} - {summary}")
        
        return "\n\n".join(citas_info)
        
    except HttpError as err:
        return f"Error al consultar las citas del día: {err}"

@function_tool
def obtener_fecha_actual() -> str:
    """Obtiene la fecha actual en formato legible y también en formato YYYY-MM-DD para programar citas."""
    ahora = datetime.datetime.now()
    fecha_legible = ahora.strftime("%d de %B de %Y")
    fecha_formato = ahora.strftime("%Y-%m-%d")
    hora_actual = ahora.strftime("%H:%M")
    
    return f"📅 Fecha actual: {fecha_legible}\n🕒 Hora actual: {hora_actual}\n💡 Formato para programar citas: {fecha_formato}"

@function_tool
def mostrar_slots_libres(fecha: str) -> str:
    """Muestra únicamente los horarios disponibles en formato simple para una fecha específica."""
    service = _init_service()
    
    try:
        # Parsear la fecha proporcionada
        target_date = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        
        # Verificar que no sea un día pasado
        if target_date < datetime.datetime.now().date():
            return "❌ No se pueden consultar citas en fechas pasadas."
            
    except ValueError:
        return "❌ Error: Formato de fecha incorrecto. Use el formato YYYY-MM-DD (ej: 2025-07-15)"
    
    # Definir horarios laborales (cada 30 minutos)
    slots_manana = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30"]
    slots_tarde = ["15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
    
    # Obtener eventos existentes para el día
    time_min = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
    time_max = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"
    
    try:
        events = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute().get("items", [])
        
        # Extraer horarios ocupados
        horarios_ocupados = []
        for event in events:
            start_time = event['start'].get('dateTime')
            if start_time:
                dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                horarios_ocupados.append(dt.time().strftime("%H:%M"))
        
        # Filtrar horarios disponibles
        libres_manana = [h for h in slots_manana if h not in horarios_ocupados]
        libres_tarde = [h for h in slots_tarde if h not in horarios_ocupados]
        
        fecha_formateada = target_date.strftime("%d/%m/%Y")
        
        if not libres_manana and not libres_tarde:
            return f"Sin horarios disponibles para el {fecha_formateada}"
        
        resultado = []
        if libres_manana:
            resultado.append("Mañanas: " + " • ".join(libres_manana))
        if libres_tarde:
            resultado.append("Tardes: " + " • ".join(libres_tarde))
        
        return f"Horarios libres {fecha_formateada}:\n" + "\n".join(resultado)
        
    except HttpError as err:
        return f"❌ Error al consultar: {err}"