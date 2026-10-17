import os
import time
import streamlit as st
from pypdf import PdfReader
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Asistente de Maestría")
st.title("Asistente Virtual - Maestría en Gestión de Negocios")
st.write("Consulta información oficial sobre convocatorias, plan de estudios, horarios y costos.")

@st.cache_resource
def cargar_contexto_documentos():
    texto_total = ""
    folder_path = "documentos"
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".pdf"):
                reader = PdfReader(os.path.join(folder_path, file))
                for page in reader.pages:
                    texto = page.extract_text()
                    if texto:
                        texto_total += texto + "\n"
    
    # Comprime espacios en blanco para reducir el uso de tokens
    return " ".join(texto_total.split())

contexto_pdf = cargar_contexto_documentos()


system_instruction = f"""
Eres un asistente virtual oficial para la Maestría en Gestión de Negocios.
Tu objetivo es responder las dudas de los aspirantes de forma amable, clara y profesional.

REGLAS:
1. Responde ÚNICAMENTE utilizando la información provista en el siguiente contexto.
2. Si la respuesta NO está en el contexto, responde: "No dispongo de esa información. Te sugiero contactar directamente a la coordinación."
3. NO inventes datos.

CONTEXTO OFICIAL DE LA MAESTRÍA:
{contexto_pdf}
"""


def consultar_gemini_con_reintentos(prompt):
    # Modelos candidatos en orden de prioridad
    modelos = ["gemini-3.8-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    
    for modelo in modelos:
        for intento in range(3):  # Hasta 3 reintentos por modelo
            try:
                response = client.models.generate_content(
                    model=modelo,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.1,
                    ),
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                err_str = str(e)
                # Si el servidor responde 503 (saturación), realiza una pausa de 2 segundos y reintenta
                if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str:
                    time.sleep(2 * (intento + 1))
                    continue
                else:
                    # Si el modelo no existe o falla por otro motivo, pasa al siguiente modelo
                    break

    return "⚠️ El servidor de Google está experimentando alta demanda en este momento. Por favor, reintenta tu pregunta en unos segundos."


if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de pregunta del usuario
if user_input := st.chat_input("Escribe tu duda sobre la maestría aquí..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generar respuesta gestionando los reintentos
    with st.chat_message("assistant"):
        with st.spinner("Consultando información oficial..."):
            bot_response = consultar_gemini_con_reintentos(user_input)

        st.markdown(bot_response)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})