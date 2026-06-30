#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar APK automáticamente usando PWA Builder
Abre el navegador con la URL lista para generar el APK
"""

import webbrowser
import time
import subprocess
import sys
import os

def print_banner():
    print()
    print("=" * 60)
    print("  GENERADOR DE APK - PWA BUILDER")
    print("=" * 60)
    print()

def abrir_pwabuilder():
    """Abre PWA Builder con la URL de la app"""
    
    # URL de la app (localhost para desarrollo)
    url_app = "http://localhost:5000"
    
    # URL de PWA Builder con parámetros
    url_pwabuilder = f"https://pwabuilder.com/?url={url_app}&platform=android"
    
    print("  Abriendo PWA Builder en tu navegador...")
    print(f"  URL de la app: {url_app}")
    print()
    
    # Abrir en navegador
    webbrowser.open(url_pwabuilder)
    
    print("=" * 60)
    print("  PASOS PARA GENERAR EL APK:")
    print("=" * 60)
    print()
    print("  1. En el navegador que se abrio:")
    print("     - PWA Builder analizara tu app automaticamente")
    print("     - Haz clic en 'Generate Package' o 'Build'")
    print()
    print("  2. Selecciona 'Android' como plataforma")
    print()
    print("  3. Haz clic en 'Download' para descargar el APK")
    print()
    print("  4. El APK se descargara en tu carpeta de Descargas")
    print()
    print("  5. Instala el APK en tu celular:")
    print("     - Transfiere el archivo .apk a tu celular")
    print("     - Abrelo y acepta instalar")
    print("     - La app aparecera en tu menu de aplicaciones")
    print()
    print("=" * 60)
    print()
    print("  NOTA: La app necesita que el servidor este")
    print("  ejecutandose para funcionar.")
    print()
    print("  Si el servidor no esta corriendo, ejecuta:")
    print('    python "Sistema de Prediccion de Desercion 1.2/app_web/server.py"')
    print()
    print("=" * 60)
    print()
    input("  Presiona Enter para cerrar...")

if __name__ == '__main__':
    print_banner()
    
    # Verificar que el servidor esté corriendo
    import urllib.request
    try:
        urllib.request.urlopen('http://localhost:5000', timeout=2)
        print("  Servidor detectado en http://localhost:5000")
    except:
        print("  ADVERTENCIA: No se detecto el servidor en http://localhost:5000")
        print()
        respuesta = input("  Deseas iniciar el servidor ahora? (s/n): ").lower()
        if respuesta == 's':
            print()
            print("  Iniciando servidor...")
            server_path = os.path.join(os.path.dirname(__file__), 'server.py')
            subprocess.Popen(
                f'python "{server_path}"',
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print("  Esperando 5 segundos...")
            time.sleep(5)
    
    abrir_pwabuilder()