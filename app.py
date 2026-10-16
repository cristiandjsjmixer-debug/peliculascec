from flask import Flask, request, redirect
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def obtener_enlace_fresco(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Referer': url
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        html = response.text
        
        # 1. Buscar enlaces directos de video (.mp4 o .m3u8) en el código fuente
        match_video = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', html)
        if match_video:
            return match_video.group(0)
            
        # 2. Si usa BeautifulSoup, buscar etiquetas <source> o reproductores comunes
        soup = BeautifulSoup(html, 'html.parser')
        source_tag = soup.find('source')
        if source_tag and source_tag.get('src'):
            return source_tag['src']
            
        # 3. Buscar URLs ocultas en scripts de reproducción o iframes
        iframe_tag = soup.find('iframe')
        if iframe_tag and iframe_tag.get('src'):
            iframe_url = iframe_tag['src']
            if not iframe_url.startswith('http'):
                # Manejar URLs relativas si las hubiera
                if iframe_url.startswith('//'):
                    iframe_url = 'https:' + iframe_url
            # Opcional: recursivo o lectura del iframe si es necesario
            return iframe_url

        return None
    except Exception as e:
        print(f"Error en extraccion: {str(e)}")
        return None

@app.route('/ver')
def ver_pelicula():
    url_original = request.args.get('url')
    if not url_original:
        return "Falta el enlace de la película", 400
    
    enlace_fresco = obtener_enlace_fresco(url_original)
    if enlace_fresco:
        # Redirige al enlace directo o reproductor encontrado
        return redirect(enlace_fresco)
    else:
        return "Error al procesar el video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
