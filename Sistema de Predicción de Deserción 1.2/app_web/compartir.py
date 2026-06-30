#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para COMPARTIR la app por internet automáticamente.
Inicia el servidor Flask + túnel ngrok en un solo comando.
"""

import sys
import os
import subprocess
import time
import webbrowser
import threading
import signal

# Agregar el path de los scripts de Python (donde está ngrok.exe)
scripts_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 
                            'Python', 'pythoncore-3.14-64', 'Scripts')
if os.path.exists(scripts_path):
    os.environ['PATH'] = scripts_path + os.pathsep + os.environ.get('PATH', '')

# ─── FUNCIONES ──────────────────────────────────────────────

def print_banner():
    print()
    print("=" * 60)
    print("  COMPARTIR APP - SISTEMA DE PREDICCION DE DESERCION")
    print("=" * 60)
    print()

def iniciar_servidor():
    """Inicia el servidor Flask en segundo plano"""
    server_path = os.path.join(os.path.dirname(__file__), 'server.py')
    # Usar shell=True para evitar problemas de rutas con espacios
    process = subprocess.Popen(
        f'python "{server_path}"',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW  # No muestra ventana de cmd
    )
    return process

def esperar_servidor():
    """Espera a que el servidor Flask esté listo"""
    import urllib.request
    for i in range(30):  # Esperar máximo 30 segundos
        try:
            urllib.request.urlopen('http://127.0.0.1:5000')
            return True
        except:
            time.sleep(1)
    return False

def iniciar_ngrok():
    """Inicia ngrok y devuelve la URL pública"""
    try:
        # Intentar usar pyngrok
        from pyngrok import ngrok
        
        print("  Iniciando tunel ngrok...")
        # Abrir túnel en el puerto 5000
        tunel = ngrok.connect(5000, "http")
        url_publica = tunel.public_url
        
        return url_publica
        
    except Exception as e:
        print(f"  Error con pyngrok: {e}")
        print()
        print("  Intentando con ngrok directamente...")
        
        try:
            # Buscar ngrok.exe
            posibles_paths = [
                os.path.join(scripts_path, 'ngrok.exe'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Desktop', 'ngrok.exe'),
                os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads', 'ngrok.exe'),
                'ngrok.exe',
            ]
            
            ngrok_path = None
            for p in posibles_paths:
                if os.path.exists(p):
                    ngrok_path = p
                    break
            
            if not ngrok_path:
                return None
            
            # Iniciar ngrok en segundo plano
            subprocess.Popen(
                f'"{ngrok_path}" http 5000 --log=stdout',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(3)
            
            # Obtener la URL desde la API local de ngrok
            import urllib.request
            import json
            
            for i in range(10):
                try:
                    response = urllib.request.urlopen('http://127.0.0.1:4040/api/tunnels')
                    data = json.loads(response.read())
                    url_publica = data['tunnels'][0]['public_url']
                    return url_publica
                except:
                    time.sleep(2)
            
            return None
            
        except Exception as e2:
            print(f"  Error: {e2}")
            return None

def abrir_ngrok_dashboard():
    """Abre el dashboard de ngrok en el navegador"""
    try:
        webbrowser.open('http://127.0.0.1:4040')
    except:
        pass

# ─── MAIN ───────────────────────────────────────────────────

def main():
    print_banner()
    
    print("  [1/3] Iniciando servidor Flask...")
    servidor = iniciar_servidor()
    
    print("  [2/3] Esperando que el servidor este listo...")
    if not esperar_servidor():
        print("  ERROR: No se pudo iniciar el servidor.")
        print("  Intente ejecutar manualmente:")
        print('    python "Sistema de Prediccion de Desercion 1.2/app_web/server.py"')
        return
    
    print("  [3/3] Creando tunel a internet...")
    url = iniciar_ngrok()
    
    print()
    print("=" * 60)
    
    if url:
        print(f"  URL PUBLICA (COMPARTE ESTE ENLACE):")
        print(f"  {url}")
        print()
        print("  Cuaquier persona con este enlace puede")
        print("  usar la app desde su navegador.")
        print()
        print("  El enlace estara activo mientras esta")
        print("  ventana este abierta.")
        print()
        print("  Dashboard ngrok: http://127.0.0.1:4040")
        print("  (para ver estadisticas de conexion)")
        
        # Abrir automáticamente en el navegador
        webbrowser.open(url)
    else:
        print("  NO se pudo crear el tunel automaticamente.")
        print()
        print("  Usa estas opciones manuales:")
        print()
        print("  Opcion 1 - ngrok (recomendada):")
        print("    1. Descarga ngrok.exe de https://ngrok.com")
        print("    2. Colocalo en tu Escritorio")
        print("    3. Ejecuta en otra terminal:")
        print('       cd Desktop')
        print('       ngrok http 5000')
        print()
        print("  Opcion 2 - Local (solo misma red):")
        print(f"    http://{obtener_ip_local()}:5000")
    
    print("=" * 60)
    print()
    print("  Presiona CTRL+C para detener todo")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("  Deteniendo...")
        
        # Detener ngrok
        try:
            from pyngrok import ngrok
            ngrok.kill()
        except:
            pass
        
        # Detener servidor Flask
        servidor.terminate()
        
        print("  Aplicacion detenida.")
        print()

def obtener_ip_local():
    import socket
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


if __name__ == '__main__':
    main()