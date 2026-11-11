"""Servidor FastAPI que recibe los mensajes de WhatsApp desde Twilio."""
import logging
import os
import time
from collections import defaultdict, deque

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

import bot

load_dotenv()
log = logging.getLogger("webhook")
app = FastAPI(title="Chatbot Maestría - WhatsApp")

AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
VALIDAR = os.getenv("VALIDATE_TWILIO", "true").lower() == "true"
LIMITE, VENTANA = 10, 60  # 10 mensajes por minuto por numero
_visitas: dict[str, deque] = defaultdict(deque)


def _excede_limite(numero: str) -> bool:
    ahora = time.time()
    q = _visitas[numero]
    while q and ahora - q[0] > VENTANA:
        q.popleft()
    q.append(ahora)
    return len(q) > LIMITE


def _partir(texto: str, tam: int = 1500) -> list[str]:
    """WhatsApp/Twilio limita ~1600 caracteres por mensaje."""
    partes, actual = [], ""
    for linea in texto.split("\n"):
        if len(actual) + len(linea) + 1 > tam and actual:
            partes.append(actual.strip())
            actual = ""
        actual += linea + "\n"
    if actual.strip():
        partes.append(actual.strip())
    return partes or [texto[:tam]]


@app.get("/")
def salud():
    return {"estado": "ok", "documentos_cargados": bool(bot.CONTEXTO)}


@app.post("/whatsapp")
async def whatsapp(request: Request):
    form = dict(await request.form())

    if VALIDAR:
        firma = request.headers.get("X-Twilio-Signature", "")
        if not RequestValidator(AUTH_TOKEN).validate(f"{PUBLIC_URL}/whatsapp", form, firma):
            log.warning("Firma de Twilio invalida")
            return Response(status_code=403)

    numero = form.get("From", "desconocido")
    texto = form.get("Body", "")
    twiml = MessagingResponse()

    if _excede_limite(numero):
        twiml.message("Estás enviando mensajes muy rápido 😅 Espera un momento e intenta de nuevo.")
    else:
        respuesta = await run_in_threadpool(bot.responder, numero, texto)
        for parte in _partir(respuesta):
            twiml.message(parte)

    return Response(content=str(twiml), media_type="application/xml")
