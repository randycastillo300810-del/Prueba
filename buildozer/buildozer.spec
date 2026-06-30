[app]

# ─── INFORMACIÓN BÁSICA ─────────────────────────────────────
title = Sistema de Predicción de Deserción
package.name = predesercion
package.domain = org.predesercion
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,css,js,json,pkl
version = 1.0
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# ─── ORIENTACIÓN Y TEMA ─────────────────────────────────────
orientation = portrait
fullscreen = 0
android.arch = armeabi-v7a
android.api = 21
android.minapi = 21
android.sdk = 21
android.ndk = 23b

# ─── ICONO Y NOMBRE ─────────────────────────────────────────
icon.filename = %(source.dir)s/static/icon.png
presplash.filename = %(source.dir)s/static/splash.png

# ─── DEPENDENCIAS PYTHON ────────────────────────────────────
requirements = python3==3.9.13,flask==2.3.3,scikit-learn==1.3.0,pandas==2.0.3,numpy==1.24.3,joblib==1.3.2,werkzeug==2.3.7,markupsafe==2.1.3,itsdangerous==2.1.2,blinker==1.6.2,click==8.1.6,jinja2==3.1.2,threadpoolctl==3.2.0,scipy==1.10.1,psutil==5.9.5

# ─── BOOTSTRAP (WebView) ─────────────────────────────────────
# ESTO ES OBLIGATORIO - Usa WebView para mostrar el HTML/CSS/JS
bootstrap = webview

# ─── PERMISOS ANDROID ───────────────────────────────────────
# INTERNET es necesario para que el WebView cargue contenido local
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# ─── CONFIGURACIÓN DEL WEBVIEW ──────────────────────────────
# URL que carga al abrir la app (localhost porque el servidor Flask corre internamente)
webview_url = http://localhost:5000/

# ─── CONFIGURACIÓN ADICIONAL ────────────────────────────────
# No mostrar barra de estado Android
android.statusbar_color = #1a1a2e
android.statusbar_style = dark

# Log level para debugging
log_level = 2

# ─── OPCIONES DE COMPILACIÓN ────────────────────────────────
# No incluir fuentes de Python (reduce tamaño)
no-python = 0

# Incluir archivos adicionales
android.add_src = 

# ─── FIRMA DE LA APK (opcional) ─────────────────────────────
# Para publicar en Play Store necesitas configurar esto
# android.keystore = 
# android.keyalias = 
# android.keystore_password = 
# android.keyalias_password = 

# ─── META-DATOS ─────────────────────────────────────────────
# Información que aparece en Play Store
title = Sistema de Predicción de Deserción
author = Tu Nombre
author_email = tu@email.com
url = https://github.com/tu-usuario/predesercion
description = Sistema de predicción de deserción universitaria usando Machine Learning. 100% offline.