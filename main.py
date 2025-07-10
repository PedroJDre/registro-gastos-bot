from fastapi import FastAPI, Request
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime
from fastapi.responses import PlainTextResponse

app = FastAPI()

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open(os.environ["GOOGLE_SHEET_NAME"]).sheet1

# OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

def procesar_mensaje(texto):
    prompt = f"Extraé monto, categoría y fecha (hoy por defecto) del siguiente texto de gasto: '{texto}'. Respondé en formato JSON con keys: monto, categoria, fecha (YYYY-MM-DD)"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content
    return eval(content)

@app.post("/webhook")
async def webhook(request: Request):
    form = await request.form()
    mensaje = form.get("Body")
    if not mensaje:
        return PlainTextResponse("No message received", status_code=400)

    try:
        data = procesar_mensaje(mensaje)
        fecha = data.get("fecha", datetime.today().strftime("%Y-%m-%d"))
        monto = data.get("monto", "")
        categoria = data.get("categoria", "")
        sheet.append_row([fecha, monto, categoria, mensaje])
        return PlainTextResponse("Gasto registrado con éxito.")
    except Exception as e:
        return PlainTextResponse(f"Error: {str(e)}", status_code=500)
