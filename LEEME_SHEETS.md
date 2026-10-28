# Lista de estudiantes en Google Sheets

La hoja es **privada**: solo la lee el bot, mediante una cuenta de servicio. No la publiques en la web.
Cualquier cambio que hagas en la hoja (agregar o borrar filas) se aplica en máximo 60 segundos, sin reiniciar la app.

## 1. Crear la hoja
1. Crea una hoja de cálculo de Google.
2. En la fila 1 pon los encabezados: `matricula` y `correo` (la columna `correo` puede quedar vacía).
3. Una fila por estudiante. Con la matrícula basta.
4. Formato de la columna `matricula`: selecciónala → Formato → Número → **Texto sin formato** (así no se pierden ceros a la izquierda).

## 2. Crear la cuenta de servicio (una sola vez)
1. Entra a https://console.cloud.google.com y crea un proyecto (o usa uno existente).
2. Menú **APIs y servicios → Biblioteca** → busca **Google Sheets API** → **Habilitar**.
3. **APIs y servicios → Credenciales → Crear credenciales → Cuenta de servicio**. Ponle un nombre y créala (no necesita roles).
4. Abre la cuenta creada → pestaña **Claves → Agregar clave → Crear clave nueva → JSON**. Se descarga un archivo.
5. Guarda ese archivo junto a `app.py` con el nombre `credenciales_google.json`. **No lo subas a GitHub** (ya está en `.gitignore`).
6. Dentro del JSON busca `client_email` (algo como `bot@proyecto.iam.gserviceaccount.com`).

## 3. Compartir la hoja con el bot
En la hoja: **Compartir** → pega el `client_email` → permiso **Lector** → Enviar.

## 4. Configurar `.env`
```
GOOGLE_SHEET_ID=<lo que va entre /d/ y /edit en la URL de la hoja>
GOOGLE_SHEET_TAB=            # nombre de la pestaña; vacío = la primera
GOOGLE_CREDENTIALS_FILE=credenciales_google.json
```

## Si despliegas en Streamlit Community Cloud
No subas el JSON. En **Settings → Secrets** pega el contenido del JSON así:
```
[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "..."
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```
y agrega `GOOGLE_SHEET_ID` y `GEMINI_API_KEY` también en Secrets (o como variables de entorno).

## Comportamiento
- Si Google falla un momento, el bot usa la última copia buena de la lista.
- Si no hay lista y nunca se pudo leer, el acceso de estudiantes se cierra (no deja entrar a nadie).
- Si `GOOGLE_SHEET_ID` está vacío, se usa `estudiantes_autorizados.csv` como respaldo.
- Los errores reales (hoja no compartida, clave inválida, etc.) se ven en la consola donde corre la app.
