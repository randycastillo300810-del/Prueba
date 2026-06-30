#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Flask para APK Android - Buildozer
Carga el modelo ML y sirve el frontend
"""

import os
import sys
import json
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory

# Agregar el directorio padre al path para importar modelos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__)

# ─── CONFIGURACIÓN ──────────────────────────────────────────
MODELO_PATH = os.path.join(os.path.dirname(__file__), 'modelo_desercion.pkl')
app.config['MODELO_PATH'] = MODELO_PATH

# ─── VARIABLES GLOBALES ─────────────────────────────────────
modelo = None
scaler = None
columnas_modelo = None

def cargar_modelo():
    """Carga el modelo de Machine Learning"""
    global modelo, scaler, columnas_modelo
    
    try:
        import joblib
        
        if not os.path.exists(MODELO_PATH):
            print(f"ADVERTENCIA: No se encontró el modelo en {MODELO_PATH}")
            print("La app funcionará pero sin predicciones ML")
            return False
        
        datos = joblib.load(MODELO_PATH)
        
        # El modelo puede ser un diccionario o el modelo directamente
        if isinstance(datos, dict):
            modelo = datos.get('modelo')
            scaler = datos.get('scaler')
            columnas_modelo = datos.get('columnas', [])
        else:
            modelo = datos
            scaler = None
            columnas_modelo = []
        
        print(f"✓ Modelo cargado: {MODELO_PATH}")
        print(f"  - Columnas: {columnas_modelo}")
        return True
        
    except Exception as e:
        print(f"Error al cargar modelo: {e}")
        traceback.print_exc()
        return False

# Cargar modelo al iniciar
cargar_modelo()

# ─── RUTAS ──────────────────────────────────────────────────

@app.route('/')
def index():
    """Sirve la página principal"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Sirve archivos estáticos (CSS, JS, imágenes)"""
    return send_from_directory('static', path)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de predicción"""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Validar datos recibidos
        campos_requeridos = ['promedio', 'asistencia', 'materias_reprobadas']
        for campo in campos_requeridos:
            if campo not in datos:
                return jsonify({'error': f'Falta el campo: {campo}'}), 400
        
        # Si no hay modelo, retornar predicción simulada
        if modelo is None:
            promedio = float(datos.get('promedio', 0))
            asistencia = float(datos.get('asistencia', 0))
            materias_reprobadas = int(datos.get('materias_reprobadas', 0))
            
            # Lógica simple de predicción sin modelo
            riesgo = 0
            if promedio < 10:
                riesgo += 40
            if asistencia < 70:
                riesgo += 30
            if materias_reprobadas >= 2:
                riesgo += 30
            
            riesgo = min(riesgo, 100)
            deserta = riesgo > 50
            
            return jsonify({
                'riesgo': riesgo,
                'deserta': deserta,
                'mensaje': 'Predicción sin modelo ML (modo básico)'
            })
        
        # Preparar datos para el modelo
        import pandas as pd
        import numpy as np
        
        # Crear DataFrame con los datos
        df = pd.DataFrame([datos])
        
        # Aplicar scaler si existe
        if scaler is not None:
            df_scaled = scaler.transform(df[columnas_modelo])
            df[columnas_modelo] = df_scaled
        
        # Hacer predicción
        probabilidad = modelo.predict_proba(df)[0]
        clase = modelo.predict(df)[0]
        
        # Determinar riesgo
        riesgo = round(probabilidad[1] * 100, 1) if len(probabilidad) > 1 else round(probabilidad[0] * 100, 1)
        
        return jsonify({
            'riesgo': riesgo,
            'deserta': bool(clase),
            'mensaje': 'Predicción con modelo ML'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Endpoint de salud para verificar que el servidor funciona"""
    return jsonify({
        'status': 'ok',
        'modelo_cargado': modelo is not None
    })

# ─── INICIAR SERVIDOR ───────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("  SERVIDOR FLASK - APK ANDROID")
    print("=" * 60)
    print(f"\n  Modelo: {'Cargado ✓' if modelo else 'No disponible (modo básico)'}")
    print(f"  Ruta: http://0.0.0.0:5000")
    print(f"\n  Presiona CTRL+C para detener")
    print("=" * 60)
    
    # Modo producción
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)