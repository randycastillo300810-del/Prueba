# 📱 Guía Completa: APK Android con Buildozer

## 📋 Estructura de Carpetas

```
buildozer/
├── main.py                    # Servidor Flask principal
├── buildozer.spec            # Configuración de Buildozer
├── modelo_desercion.pkl      # ← TU MODELO ML (colócalo aquí)
├── templates/
│   └── index.html            # Frontend HTML
├── static/
│   ├── css/
│   │   └── style.css         # Estilos CSS
│   ├── js/
│   │   └── app.js            # Lógica JavaScript
│   └── icon.png              # Icono de la app (opcional)
└── .buildozer/               # Se crea automáticamente
```

---

## 🔧 Paso 1: Preparar el Modelo

### Coloca tu modelo en la carpeta correcta:

```bash
# Copia tu modelo .pkl a la carpeta buildozer/
cp tu_modelo_entrenado.pkl "Sistema de Predicción de Deserción 1.2/app_web/buildozer/modelo_desercion.pkl"
```

**Importante:** El modelo debe ser un archivo `.pkl` guardado con `joblib` o `pickle`.

**Formato esperado del modelo:**
```python
# Opción 1: Diccionario (recomendado)
{
    'modelo': modelo_sklearn,
    'scaler': StandardScaler(),
    'columnas': ['promedio', 'asistencia', 'materias_reprobadas', ...]
}

# Opción 2: Modelo directamente
modelo_sklearn  # RandomForest, XGBoost, etc.
```

---

## 🐧 Paso 2: Instalar Buildozer (WSL2 o Linux)

### En WSL2 (Windows Subsystem for Linux):

```bash
# 1. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias del sistema
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk python3-dev libffi-dev libssl-dev

# 3. Instalar Buildozer
pip3 install --user buildozer

# 4. Instalar dependencias de Android
sudo apt install -y autoconf automake libtool pkg-config libncurses5-dev libncursesw5-dev
```

### En Linux nativo:

```bash
# 1. Instalar dependencias
sudo apt update
sudo apt install -y python3-pip git zip unzip openjdk-17-jdk python3-dev libffi-dev libssl-dev

# 2. Instalar Buildozer
pip3 install --user buildozer

# 3. Aceptar licencias de Android
yes | ~/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager --licenses
```

---

## 📁 Paso 3: Copiar Archivos del Frontend

### Copia tus archivos HTML/CSS/JS a la carpeta buildozer:

```bash
# Desde la carpeta app_web/
cp index.html buildozer/templates/
cp -r static/css/style.css buildozer/static/css/
cp -r static/js/app.js buildozer/static/js/
```

**O si tienes otros archivos:**
```bash
# Si tienes más archivos CSS/JS
cp static/css/otro.css buildozer/static/css/
cp static/js/otro.js buildozer/static/js/

# Si tienes imágenes
cp -r static/images buildozer/static/
```

---

## ⚙️ Paso 4: Configurar buildozer.spec

Edita el archivo `buildozer.spec` con tu información:

```ini
# Cambia estos valores:
title = Tu Nombre de la App
package.name = nombre_app
package.domain = com.tuempresa
version = 1.0

# Si tienes icono:
icon.filename = %(source.dir)s/static/icon.png

# Si tienes pantalla de carga:
presplash.filename = %(source.dir)s/static/splash.png
```

---

## 🚀 Paso 5: Construir la APK

### Comandos para construir:

```bash
# 1. Navega a la carpeta buildozer
cd "Sistema de Predicción de Deserción 1.2/app_web/buildozer"

# 2. Inicializar Buildozer (solo la primera vez)
buildozer init

# 3. Construir la APK (debug - para pruebas)
buildozer -v android debug

# 4. O construir APK de release (para distribuir)
buildozer -v android release
```

**Tiempo de compilación:** 15-30 minutos la primera vez (descarga dependencias)

---

## 📲 Paso 6: Instalar y Probar

### Encontrar la APK generada:

```bash
# La APK estará en:
ls bin/*.apk
```

### Instalar en el teléfono:

```bash
# Opción 1: USB (necesitas USB debugging activado)
buildozer android deploy run

# Opción 2: Manual
# 1. Copia el archivo .apk a tu celular
# 2. Abre el archivo en el celular
# 3. Acepta instalar apps de fuentes desconocidas
# 4. ¡Listo!
```

---

## 🐛 Solución de Problemas Comunes

### Error 1: `libffi` no compila

```bash
# Solución:
sudo apt install -y libffi-dev
sudo apt install -y libssl-dev
sudo apt install -y python3-dev
```

### Error 2: La app se cierra al abrir

```bash
# Ver logs:
adb logcat | grep python

# Causas comunes:
# - Error en el código Python
# - Falta el modelo .pkl
# - Ruta incorrecta del modelo
```

### Error 3: WebView no carga contenido

```ini
# En buildozer.spec, verifica:
webview_url = http://localhost:5000/

# Asegúrate de que main.py tenga:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Error 4: Error de CORS

```python
# En main.py, agrega CORS:
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Esto permite todas las conexiones
```

### Error 5: No encuentra el modelo

```python
# Verifica la ruta en main.py:
MODELO_PATH = os.path.join(os.path.dirname(__file__), 'modelo_desercion.pkl')

# Asegúrate de que el archivo existe:
import os
print(os.path.exists(MODELO_PATH))  # Debe retornar True
```

### Error 6: Compilación muy lenta

```bash
# Usa versión debug para desarrollo:
buildozer android debug

# La versión release tarda más pero es más pequeña
buildozer android release
```

---

## 📦 Dependencias Incluidas

El archivo `buildozer.spec` incluye:

- **Flask 2.3.3** - Servidor web
- **scikit-learn 1.3.0** - Machine Learning
- **pandas 2.0.3** - Manipulación de datos
- **numpy 1.24.3** - Operaciones numéricas
- **joblib 1.3.2** - Guardar/cargar modelo
- **werkzeug 2.3.7** - WSGI para Flask

---

## ✅ Checklist Pre-Compilación

Antes de compilar, verifica:

- [ ] El modelo `.pkl` está en `buildozer/modelo_desercion.pkl`
- [ ] Los archivos HTML/CSS/JS están en `templates/` y `static/`
- [ ] `buildozer.spec` tiene tu información (nombre, dominio, versión)
- [ ] Estás en WSL2 o Linux (Buildozer no funciona en Windows nativo)
- [ ] Tienes conexión a internet (solo para la primera compilación)

---

## 🎯 Comandos Rápidos

```bash
# Limpiar compilación anterior
buildozer android clean

# Compilar debug (rápido, para pruebas)
buildozer -v android debug

# Compilar release (optimizado, para distribución)
buildozer -v android release

# Instalar directamente en dispositivo USB
buildozer android deploy run

# Ver logs en tiempo real
adb logcat | grep python
```

---

## 📝 Notas Importantes

1. **100% Offline:** La app NO necesita internet después de instalada
2. **Tamaño:** La APK pesará ~50-80 MB (incluye Python + librerías)
3. **Compatibilidad:** Android 5.0 (API 21) o superior
4. **Arquitectura:** ARMv7 (funciona en la mayoría de celulares)
5. **Primera compilación:** Tarda 20-30 minutos (descarga Android SDK)
6. **Compilaciones siguientes:** 5-10 minutos

---

## 🆘 Ayuda Adicional

Si tienes problemas:

1. Revisa los logs: `adb logcat | grep python`
2. Verifica que el modelo sea compatible con las versiones de scikit-learn
3. Asegúrate de que todas las rutas sean correctas
4. Prueba primero en modo debug antes de release

---

**¡Listo para compilar!** 🚀

Ejecuta: `buildozer android debug`