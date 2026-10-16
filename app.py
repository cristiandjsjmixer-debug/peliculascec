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
        
        # Imprimir un pedazo del HTML en los logs de Render para analizarlo
        print("HTML obtenido (primeros 300 caracteres):", html[:300])
        
        # Buscar cualquier enlace dentro de scripts o etiquetas que parezca un stream
        match_video = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8|ts)', html)
        if match_video:
            return match_video.group(0)
            
        # Buscar si hay URLs en fuentes o iframes
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar en todas las etiquetas script por enlaces de video
        for script in soup.find_all('script'):
            if script.string:
                match_script = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', script.string)
                if match_script:
                    return match_script.group(0)

        return None
    except Exception as e:
        print(f"Excepción detallada: {str(e)}")
        return None

@app.route('/ver')
def ver_pelicula():
    url_original = request.args.get('url')
    if not url_original:
        return "Falta el enlace de la película", 400
    
    enlace_fresco = obtener_enlace_fresco(url_original)
    if enlace_fresco:
        return redirect(enlace_fresco)
    else:
        return "Error al procesar el video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
