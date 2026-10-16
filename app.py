from flask import Flask, request, redirect
import re
import time
import random
import string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def obtener_enlace_fresco(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }
    
    if '/d/' in url:
        url_embed = url.replace('/d/', '/e/')
    else:
        url_embed = url

    headers['Referer'] = url_embed
    try:
        res_embed = session.get(url_embed, headers=headers, timeout=10)
        html_embed = res_embed.text

        match_pass = re.search(r"/pass_md5/[^'\"?]+", html_embed)
        if not match_pass:
            return None

        pass_md5_path = match_pass.group(0)
        parsed_domain = "/".join(url_embed.split("/")[:3])
        token_endpoint = f"{parsed_domain}{pass_md5_path}"

        res_token = session.get(token_endpoint, headers=headers, timeout=10)
        base_cdn_url = res_token.text.strip()

        rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        ts = int(time.time() * 1000)
        token_id = pass_md5_path.split('/')[-1]

        direct_stream_url = f"{base_cdn_url}{rand_str}?token={token_id}&expiry={ts}"
        return direct_stream_url
    except Exception:
        return None

@app.route('/ver')
def ver_pelicula():
    url_original = request.args.get('url')
    if not url_original:
        return "Falta el enlace de la película", 400
    
    enlace_fresco = obtener_enlace_fresco(url_original)
    if enlace_fresco:
        # Redirige al reproductor directo de la CDN con el token nuevo al instante
        return redirect(enlace_fresco)
    else:
        return "Error al procesar el video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
