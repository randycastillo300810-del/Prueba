#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web simple - Solo abre index.html y funciona
"""

import http.server
import socketserver
import os
import sys

# Cambiar al directorio de la app
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Agregar headers CORS para permitir acceso a la API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

print("=" * 60)
print("  SERVIDOR WEB - SISTEMA DE PREDICCION DE DESERCION")
print("=" * 60)
print(f"\n  Abre en tu navegador:")
print(f"     http://localhost:{PORT}/index.html")
print(f"\n  Para detener: CTRL+C")
print("=" * 60)
print()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
        sys.exit(0)