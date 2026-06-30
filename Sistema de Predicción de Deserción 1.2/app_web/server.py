#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Web - Sistema de Predicción de Deserción Universitaria
App híbrida: Python Flask + HTML/CSS/JS responsivo para Android
"""

import sys
import os
import json
import io
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory

# Agregar carpeta padre al path para importar modelos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.generador_datos import GeneradorDatos
from models.sistema import SistemaPrediccionDesercion
from models.lector_excel import LectorExcel

app = Flask(__name__)

# ─── ESTADO GLOBAL DEL SISTEMA ──────────────────────────────
class AppState:
    def __init__(self):
        self.sistema = None
        self.estudiantes = None
        self.generador = GeneradorDatos()

state = AppState()

# ─── RUTAS API ──────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Devuelve el estado actual del sistema"""
    if not state.estudiantes or not state.sistema:
        return jsonify({
            'activo': False,
            'total': 0,
            'en_riesgo': 0,
            'porcentaje_riesgo': 0,
            'mensaje': 'Sistema inactivo. Genere datos o cargue un Excel.'
        })
    
    total = len(state.estudiantes)
    en_riesgo = sum(1 for e in state.estudiantes if state.sistema.predecir(e)['deserta'])
    return jsonify({
        'activo': True,
        'total': total,
        'en_riesgo': en_riesgo,
        'porcentaje_riesgo': round(en_riesgo / total * 100, 1) if total > 0 else 0
    })


@app.route('/api/generar', methods=['POST'])
def generar_datos():
    """Genera datos sintéticos y entrena el sistema"""
    try:
        data = request.get_json() or {}
        n = int(data.get('cantidad', 500))
        
        state.estudiantes = state.generador.generar_dataset(n=n)
        state.sistema = SistemaPrediccionDesercion()
        state.sistema.entrenar(state.estudiantes)
        
        return jsonify({
            'exito': True,
            'mensaje': f'✅ Generados {len(state.estudiantes)} estudiantes sintéticos',
            'total': len(state.estudiantes)
        })
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'❌ Error: {str(e)}'})


@app.route('/api/cargar_excel', methods=['POST'])
def cargar_excel():
    """Carga un archivo Excel desde el formulario"""
    try:
        if 'archivo' not in request.files:
            return jsonify({'exito': False, 'mensaje': '❌ No se envió ningún archivo'})
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            return jsonify({'exito': False, 'mensaje': '❌ Nombre de archivo vacío'})
        
        # Guardar temporalmente
        temp_path = os.path.join(os.path.dirname(__file__), 'temp.xlsx')
        archivo.save(temp_path)
        
        lector = LectorExcel()
        lector.cargar_datos(temp_path)
        state.estudiantes = lector.convertir_a_estudiantes()
        
        # Eliminar temp
        try:
            os.remove(temp_path)
        except:
            pass
        
        if not state.estudiantes:
            return jsonify({'exito': False, 'mensaje': '❌ No se pudieron cargar estudiantes. Verifique el formato.'})
        
        state.sistema = SistemaPrediccionDesercion()
        state.sistema.entrenar(state.estudiantes)
        
        return jsonify({
            'exito': True,
            'mensaje': f'✅ Cargados {len(state.estudiantes)} estudiantes desde {archivo.filename}',
            'total': len(state.estudiantes)
        })
        
    except PermissionError:
        return jsonify({'exito': False, 'mensaje': '❌ Archivo en uso. Ciérrelo en Excel e intente de nuevo.'})
    except Exception as e:
        return jsonify({'exito': False, 'mensaje': f'❌ Error: {str(e)}'})


@app.route('/api/estadisticas')
def get_estadisticas():
    """Devuelve estadísticas completas"""
    if not state.sistema or not state.estudiantes:
        return jsonify({'exito': False, 'mensaje': '⚠️ Primero genere datos o cargue un Excel'})
    
    estudiantes = state.estudiantes
    total = len(estudiantes)
    notas = [e.promedio_primer_semestre for e in estudiantes]
    promedio_gen = sum(notas) / len(notas) if notas else 0
    
    en_riesgo = sum(1 for e in estudiantes if state.sistema.predecir(e)['deserta'])
    seguros = total - en_riesgo
    
    # Riesgo por rango de notas
    rangos_notas = [(0, 8, '0-8'), (8, 10, '8-10'), (10, 12, '10-12'), (12, 14, '12-14'), (14, 21, '14-20')]
    riesgo_rangos = []
    for bajo, alto, etiqueta in rangos_notas:
        grupo = [e for e in estudiantes if bajo <= e.promedio_primer_semestre < alto]
        if grupo:
            riesgo = sum(1 for e in grupo if state.sistema.predecir(e)['deserta'])
            riesgo_rangos.append({
                'rango': etiqueta,
                'total': len(grupo),
                'en_riesgo': riesgo,
                'porcentaje': round(riesgo / len(grupo) * 100, 1)
            })
    
    return jsonify({
        'exito': True,
        'total': total,
        'en_riesgo': en_riesgo,
        'seguros': seguros,
        'porcentaje_riesgo': round(en_riesgo / total * 100, 1) if total > 0 else 0,
        'promedio_global': round(promedio_gen, 1),
        'nota_min': round(min(notas), 1),
        'nota_max': round(max(notas), 1),
        'riesgo_por_rango': riesgo_rangos
    })


@app.route('/api/lista_riesgo')
def get_lista_riesgo():
    """Devuelve la lista de estudiantes en riesgo"""
    if not state.sistema or not state.estudiantes:
        return jsonify({'exito': False, 'mensaje': '⚠️ Primero genere datos o cargue un Excel'})
    
    estudiantes_riesgo = []
    for e in state.estudiantes:
        pred = state.sistema.predecir(e)
        if pred['deserta']:
            nombre = getattr(e, 'nombre_completo', f"ID {e.id}")
            cedula = getattr(e, 'cedula', '')
            
            # Materias reprobadas
            materias_reprobadas = []
            if hasattr(e, 'notas') and e.notas:
                materias_reprobadas = [m for m, n in e.notas.items() if n < 10]
            
            # Factores
            factores = []
            if e.materias_reprobadas >= 2:
                factores.append(f"{e.materias_reprobadas} materias reprobadas")
            if e.baja_asistencia:
                factores.append(f"baja asistencia ({e.asistencia_promedio}%)")
            if e.carga_alta:
                factores.append("carga alta")
            
            # Recomendación
            alerta = state.sistema.generar_alerta(e)
            recomendacion = alerta.get('recomendaciones', ['Seguimiento general'])[0] if alerta else 'Seguimiento general'
            
            estudiantes_riesgo.append({
                'id': e.id,
                'nombre': nombre,
                'cedula': cedula,
                'nota': e.promedio_primer_semestre,
                'riesgo': pred['riesgo'],
                'materias_reprobadas': materias_reprobadas,
                'factores': factores,
                'recomendacion': recomendacion
            })
    
    estudiantes_riesgo.sort(key=lambda x: x['nota'])
    
    return jsonify({
        'exito': True,
        'total': len(estudiantes_riesgo),
        'estudiantes': estudiantes_riesgo
    })


@app.route('/api/buscar')
def buscar_estudiante():
    """Busca estudiantes por nombre o cédula"""
    if not state.sistema or not state.estudiantes:
        return jsonify({'exito': False, 'mensaje': '⚠️ Primero genere datos o cargue un Excel'})
    
    texto = request.args.get('q', '').strip().lower()
    if not texto:
        return jsonify({'exito': False, 'mensaje': '⚠️ Ingrese un término de búsqueda'})
    
    resultados = []
    for e in state.estudiantes:
        nombre = (getattr(e, 'nombre_completo', '') or '').lower()
        cedula = str(getattr(e, 'cedula', '')).lower()
        if texto in nombre or texto in cedula:
            pred = state.sistema.predecir(e)
            alerta = state.sistema.generar_alerta(e)
            nombre_est = getattr(e, 'nombre_completo', f"ID {e.id}")
            cedula_est = getattr(e, 'cedula', 'N/A')
            
            info_parts = []
            if hasattr(e, 'carrera') and e.carrera:
                info_parts.append(f"Carrera: {e.carrera}")
            if hasattr(e, 'turno') and e.turno:
                info_parts.append(f"Turno: {e.turno}")
            
            # Notas por materia
            notas_materias = {}
            if hasattr(e, 'notas') and e.notas:
                notas_materias = {m: n for m, n in e.notas.items()}
            
            resultados.append({
                'id': e.id,
                'nombre': nombre_est,
                'cedula': cedula_est,
                'nota_promedio': e.promedio_primer_semestre,
                'deserta': pred['deserta'],
                'riesgo': pred['riesgo'],
                'factores': diag['factores'] if (diag := state.sistema.diagnosticar_estudiante(e)) else [],
                'recomendaciones': alerta.get('recomendaciones', []) if alerta else [],
                'info_adicional': ' | '.join(info_parts) if info_parts else '',
                'notas_materias': notas_materias,
                'materias_reprobadas': e.materias_reprobadas,
                'asistencia': e.asistencia_promedio,
                'trabaja': e.trabaja,
                'horas_trabajo': e.horas_trabajo if e.trabaja else 0,
            })
    
    return jsonify({
        'exito': True,
        'total': len(resultados),
        'estudiantes': resultados
    })


@app.route('/api/diagnostico/<int:estudiante_id>')
def get_diagnostico(estudiante_id):
    """Obtiene diagnóstico detallado de un estudiante"""
    if not state.sistema or not state.estudiantes:
        return jsonify({'exito': False, 'mensaje': '⚠️ Sistema no activo'})
    
    estudiante = next((e for e in state.estudiantes if e.id == estudiante_id), None)
    if not estudiante:
        return jsonify({'exito': False, 'mensaje': f'❌ Estudiante ID {estudiante_id} no encontrado'})
    
    diag = state.sistema.diagnosticar_estudiante(estudiante)
    alerta = state.sistema.generar_alerta(estudiante)
    pred = state.sistema.predecir(estudiante)
    
    nombre = getattr(estudiante, 'nombre_completo', f"ID {estudiante.id}")
    cedula = getattr(estudiante, 'cedula', 'N/A')
    
    info_parts = []
    if hasattr(estudiante, 'carrera') and estudiante.carrera:
        info_parts.append(f"Carrera: {estudiante.carrera}")
    if hasattr(estudiante, 'turno') and estudiante.turno:
        info_parts.append(f"Turno: {estudiante.turno}")
    if hasattr(estudiante, 'seccion') and estudiante.seccion:
        info_parts.append(f"Sección: {estudiante.seccion}")
    
    notas_materias = {}
    if hasattr(estudiante, 'notas') and estudiante.notas:
        notas_materias = {m: n for m, n in estudiante.notas.items()}
    
    return jsonify({
        'exito': True,
        'estudiante': {
            'id': estudiante.id,
            'nombre': nombre,
            'cedula': cedula,
            'info_adicional': ' | '.join(info_parts) if info_parts else '',
            'nota_promedio': estudiante.promedio_primer_semestre,
            'notas_materias': notas_materias,
            'promedio_final': diag.get('nota_real', estudiante.promedio_primer_semestre),
            'riesgo': pred['riesgo'],
            'deserta': pred['deserta'],
            'materias_reprobadas': estudiante.materias_reprobadas,
            'asistencia': estudiante.asistencia_promedio,
            'baja_asistencia': estudiante.baja_asistencia,
            'carga_alta': estudiante.carga_alta,
            'trabaja': estudiante.trabaja,
            'horas_trabajo': estudiante.horas_trabajo if estudiante.trabaja else 0,
            'factores': diag.get('factores', []),
            'recomendaciones': alerta.get('recomendaciones', []) if alerta else [],
        }
    })


# ─── INICIAR SERVIDOR ───────────────────────────────────────

def iniciar_ngrok():
    """Intenta iniciar ngrok automaticamente para compartir por internet"""
    try:
        from pyngrok import ngrok, conf
        
        # Verificar si ya hay un tunel activo
        try:
            tuneles = ngrok.get_tunnels()
            if tuneles:
                return tuneles[0].public_url
        except:
            pass
        
        print("  Conectando a internet via ngrok...")
        tunel = ngrok.connect(5000, "http")
        return tunel.public_url
    except Exception as e:
        return None

if __name__ == '__main__':
    import socket
    import threading
    
    # Obtener IP local
    hostname = socket.gethostname()
    ip_local = socket.gethostbyname(hostname)
    
    print("=" * 60)
    print("  SISTEMA DE PREDICCION DE DESERCION")
    print("  App Web Hibrida")
    print("=" * 60)
    print(f"\n  Servidor iniciado:")
    print(f"     Local:    http://127.0.0.1:5000")
    print(f"     Red:      http://{ip_local}:5000")
    print(f"\n  Para usar en tu celular (misma red WiFi):")
    print(f"     http://{ip_local}:5000")
    print()
    
    # Intentar ngrok en segundo plano
    url_publica = None
    try:
        url_publica = iniciar_ngrok()
    except:
        pass
    
    if url_publica:
        print(f"  COMPARTE ESTE ENLACE CON QUIEN QUIERAS:")
        print(f"  {url_publica}")
        print(f"  (El enlace estara activo mientras esto se ejecute)")
    else:
        print("  Para compartir por internet:")
        print("    1. Descarga ngrok.exe de https://ngrok.com")
        print("    2. Ponlo en tu Escritorio")
        print("    3. Abre otra terminal y ejecuta:")
        print('       cd Desktop')
        print('       ngrok http 5000')
        print(f"    4. Comparte la URL que aparecera")
    
    print()
    print("  Presiona CTRL+C para detener el servidor")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
