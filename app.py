from flask import Flask, request, redirect
import re
import requests
import traceback
from bs4 import BeautifulSoup

app = Flask(__name__)

def obtener_enlace_fresco(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }
    
    response = session.get(url, headers=headers, timeout=10)
    html = response.text
    
    match_video = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8|ts)', html)
    if match_video:
        return match_video.group(0)
        
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup.find_all('script'):
        if script.string:
            match_script = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', script.string)
            if match_script:
                return match_script.group(0)

    raise ValueError(f"No se encontró enlace de video. Fragmento del HTML recibido: {html[:300]}")

@app.route('/ver')
def ver_pelicula():
    url_original = request.args.get('url')
    if not url_original:
        return "Falta el enlace de la película", 400
    
    try:
        enlace_fresco = obtener_enlace_fresco(url_original)
        return redirect(enlace_fresco)
    except Exception as e:
        # Esto imprimirá el error técnico completo directo en tu navegador
        error_detallado = traceback.format_exc()
        return f"<pre style='color: red; font-size: 16px;'>Ocurrió este error:\n\n{error_detallado}</pre>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
