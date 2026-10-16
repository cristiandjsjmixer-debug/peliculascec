from flask import Flask, request, redirect
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def obtener_enlace_playmogo(url):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://playmogo.com/',
    }
    
    try:
        # 1. Petición inicial a la URL de PlayMoGo
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        html = response.text

        # 2. Buscar enlaces directos de video (.mp4 o .m3u8) en el texto fuente
        match_video = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', html)
        if match_video:
            return match_video.group(0)

        # 3. Analizar con BeautifulSoup para buscar etiquetas <source> o scripts
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar en etiquetas source
        source_tag = soup.find('source')
        if source_tag and source_tag.get('src'):
            return source_tag['src']

        # Buscar dentro de los scripts de la página URLs de reproducción
        for script in soup.find_all('script'):
            if script.string:
                match_script = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', script.string)
                if match_script:
                    return match_script.group(0)
                # Buscar URLs de reproductores internos comunes en variables de JS
                match_url_js = re.search(r'["\'](https?://[^"\']+\bplayer\b[^"\']*)["\']', script.string)
                if match_url_js:
                    return match_url_js.group(1)

        # 4. Buscar si hay iframes donde esté cargado el reproductor real
        iframe_tag = soup.find('iframe')
        if iframe_tag and iframe_tag.get('src'):
            iframe_url = iframe_tag['src']
            if iframe_url.startswith('//'):
                iframe_url = 'https:' + iframe_url
            
            # Petición recursiva al iframe para extraer el video de adentro
            res_iframe = session.get(iframe_url, headers=headers, timeout=10)
            if res_iframe.status_code == 200:
                html_iframe = res_iframe.text
                match_iframe_video = re.search(r'https?://[^\s\'"]+\.(mp4|m3u8)', html_iframe)
                if match_iframe_video:
                    return match_iframe_video.group(0)

        return None
    except Exception as e:
        print(f"Error procesando PlayMoGo: {str(e)}")
        return None

@app.route('/ver')
def ver_pelicula():
    url_original = request.args.get('url')
    if not url_original:
        return "Falta el enlace de la película", 400
    
    enlace_fresco = obtener_enlace_playmogo(url_original)
    if enlace_fresco:
        # Redirige de forma limpia al reproductor o video directo sin publicidad
        return redirect(enlace_fresco)
    else:
        return "Error al procesar el video de PlayMoGo", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
