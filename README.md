# Bot de Registro de Gastos vía WhatsApp

Este bot escucha mensajes en WhatsApp tipo "gasté 12.000 en nafta", los interpreta con OpenAI y los guarda en una Google Sheet.

## Cómo usar

1. Subí tu archivo `service_account.json` (clave de Google)
2. Creá un archivo `.env` basado en `.env.example`
3. Ejecutá:

```
pip install -r requirements.txt
uvicorn main:app --host=0.0.0.0 --port=10000
```

4. Conectá el endpoint `/webhook` en Twilio como webhook de mensajes entrantes.
