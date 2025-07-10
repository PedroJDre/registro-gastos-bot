import os
import json
from fastapi import FastAPI, Request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from datetime import datetime

# Inicializar FastAPI
app = FastAPI()

# Configurar claves
openai.api_key = os.getenv("OPENAI_API_KEY")
twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
google_sheet_name = os.getenv("GOOGLE_SHEET_NAME")

# Configurar credenciales de Google con SignedJwtAssertionCredentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

with open("service_account.json") as f:
    keyfile_dict = json.load(f)

creds = SignedJwtAssertionCredentials(
    keyfile_dict["client_email"],
    keyfile_dict["private_key"],
    scope
)

client = gspread.authorize(creds)
sheet = client.open(google_sheet_name).sheet1

@app.post("/webhook")
async def webhook(req: Request):
    form = await req.form()
    incoming_msg = form["Body"]
    sender = form["From"]

    # Obtener categoría y monto desde OpenAI
    prompt = f"Extraé categoría y monto del siguiente mensaje de gasto: '{incoming_msg}'. Devolvélo como 'Categoría: <categoria>, Monto: <monto>'"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    result = response.choices[0].text.strip()

    # Parsear resultado
    try:
        categoria = result.split("Categoría:")[1].split(",")[0].strip()
        monto = result.split("Monto:")[1].strip()
    except:
        categoria = "No identificado"
        monto = "0"

    # Registrar en Google Sheets
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, sender, incoming_msg, categoria, monto])

    # Responder por WhatsApp
    r = MessagingResponse()
    r.message(f"Gasto registrado ✅\nCategoría: {categoria}\nMonto: {monto}")
    return str(r)
