# Chatbot de WhatsApp – Maestría en Gestión e Innovación Educativa

Flujo: `WhatsApp → Twilio → webhook.py (FastAPI) → bot.py (Gemini + PDFs) → respuesta`
y cada pregunta se registra en `preguntas.csv`, que `panel.py` (Streamlit) agrupa por temas.

## 1. Instalación
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # y llena tus claves
```
Copia tu carpeta `documentos/` (los PDFs) a esta misma carpeta.

## 2. Twilio Sandbox (gratis, ideal para la demo)
1. Crea cuenta en https://www.twilio.com y ve a **Messaging > Try it out > Send a WhatsApp message**.
2. Desde tu WhatsApp envía el código `join xxxx-xxxx` al número del sandbox (cada asistente a la demo debe hacerlo una vez).
3. Copia tu **Auth Token** al `.env` (`TWILIO_AUTH_TOKEN`).

## 3. Arrancar el servidor y exponerlo
Terminal 1:
```bash
uvicorn webhook:app --port 8000
```
Terminal 2 (instala ngrok desde https://ngrok.com):
```bash
ngrok http 8000
```
Copia la URL `https://xxxx.ngrok-free.app` a `PUBLIC_URL` en `.env` y **reinicia uvicorn**.
En Twilio, en *Sandbox settings*, pon en "When a message comes in":
`https://xxxx.ngrok-free.app/whatsapp` (método POST).

Escribe "hola" a tu sandbox: debe salir el menú.

## 4. Panel de clusters
```bash
streamlit run panel.py
```
Sin preguntas reales muestra `preguntas_ejemplo.csv`. Cuando el bot reciba mensajes, usa `preguntas.csv` automáticamente.

## Notas
- Prueba local sin firma de Twilio: `VALIDATE_TWILIO=false` en `.env`.
- Verifica qué modelos tiene tu API key: `python -c "from google import genai; import os; [print(m.name) for m in genai.Client(api_key=os.getenv('GEMINI_API_KEY')).models.list()]"`
- El `pdf_Calendario_2026_2027.pdf` pesa 2 MB: revisa que `pypdf` extraiga bien su texto; si sale vacío o revuelto, transcribe las fechas clave a un `.txt`/.pdf simple.
- Memoria y límite de mensajes están en RAM: se reinician si reinicias el servidor.
- Para producción real (más allá del sandbox) se necesita una cuenta de WhatsApp Business aprobada.
