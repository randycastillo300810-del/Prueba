# 📱 Sistema de Predicción de Deserción - App Web Móvil

## 🚀 Inicio Rápido

### Opción 1: Un solo clic (Recomendado)
Doble clic en: **`iniciar.bat`**

Esto abrirá automáticamente la app en tu navegador.

---

## 📲 Cómo generar el APK para Android

### Método 1: PWA Builder (Más fácil - 2 minutos)

1. **Abre PWA Builder:**
   - Ve a: https://pwabuilder.com
   - O ejecuta: `python generar_apk.py`

2. **Ingresa la URL de tu app:**
   ```
   http://localhost:5000
   ```

3. **Haz clic en "Generate Package"** (PWA Builder analizará tu app)

4. **Selecciona "Android"** como plataforma

5. **Haz clic en "Download"** para descargar el APK

6. **Instala el APK en tu celular:**
   - Transfiere el archivo `.apk` a tu celular (por USB, WhatsApp, Drive, etc.)
   - Abre el archivo en tu celular
   - Acepta instalar (puede pedir permiso para instalar apps de fuentes desconocidas)
   - ¡Listo! La app aparecerá en tu menú de aplicaciones

---

### Método 2: Compartir por Internet (ngrok)

Para que alguien en otro lugar pruebe la app:

1. **Descarga ngrok:**
   - Ve a: https://ngrok.com/download
   - Descarga `ngrok.exe`
   - Ponlo en tu carpeta: `C:\Users\randy\AppData\Local\Python\pythoncore-3.14-64\Scripts\`

2. **Inicia el servidor:**
   ```powershell
   python "Sistema de Predicción de Deserción 1.2\app_web\server.py"
   ```

3. **En otra terminal, inicia ngrok:**
   ```powershell
   ngrok http 5000
   ```

4. **Copia la URL pública** que aparece (ej: `https://a1b2c3d4.ngrok.io`)

5. **Comparte esa URL** con quien quieras. Pueden abrirla en cualquier navegador.

---

## 📋 Características de la App

- ✅ **Diseño responsivo** - Funciona en celulares, tablets y PC
- ✅ **Modo oscuro** - Interfaz moderna Material Design
- ✅ **Gráficos interactivos** - Chart.js para visualizaciones
- ✅ **Búsqueda inteligente** - Por nombre o cédula
- ✅ **Diagnóstico completo** - Factores de riesgo y recomendaciones
- ✅ **PWA** - Se puede instalar como app nativa

---

## 🛠️ Estructura del Proyecto

```
app_web/
├── server.py              # Servidor Flask (API)
├── templates/
│   └── index.html         # Interfaz HTML responsiva
├── static/
│   ├── css/
│   │   └── style.css      # Estilos Material Design
│   ├── js/
│   │   └── app.js         # Lógica de la app
│   └── manifest.json      # Configuración PWA
├── generar_apk.py         # Script para generar APK
├── compartir.py           # Script para compartir por internet
└── iniciar.bat            # Inicio rápido (doble clic)
```

---

## 📱 Uso de la App

### 1. Generar Datos Sintéticos
- Carga 500 estudiantes de prueba automáticamente
- El sistema entrena el modelo de predicción

### 2. Cargar Excel Real
- Sube tu archivo `.xlsx` con datos de estudiantes
- El sistema procesa y entrena con tus datos

### 3. Dashboard de Estadísticas
- Ve gráficos de distribución de riesgo
- Estadísticas por rango de notas
- Promedios y totales

### 4. Lista de Estudiantes en Riesgo
- Todos los estudiantes marcados como "en riesgo"
- Filtro por nombre o cédula
- Factores de riesgo y recomendaciones

### 5. Búsqueda y Diagnóstico
- Busca por nombre o cédula
- Ve el perfil completo del estudiante
- Notas por materia, factores, recomendaciones

---

## 🔧 Requisitos

- Python 3.8+
- Flask (ya instalado)
- Navegador moderno (Chrome, Firefox, Edge)

---

## ⚠️ Notas Importantes

1. **El servidor debe estar corriendo** para que la app funcione
2. **Para APK:** Necesitas conexión a internet la primera vez (para generar el APK)
3. **La app funciona offline** una vez instalada, pero necesita el servidor para los datos
4. **ngrok** es temporal - el enlace cambia cada vez que reinicias

---

## 🆘 Solución de Problemas

### El servidor no inicia:
```powershell
# Verifica que Flask esté instalado
python -m pip install flask
```

### ngrok no funciona:
- Descarga ngrok.exe manualmente desde https://ngrok.com
- Ponlo en la carpeta de Scripts de Python

### El APK no se instala:
- Ve a Ajustes > Seguridad > Instalar apps desconocidas
- Activa el permiso para tu navegador

---

## 📞 Contacto

Para más información sobre el sistema de predicción, consulta la documentación en `/docs`

---

**Desarrollado con ❤️ usando Python + Flask + HTML/CSS/JS**