#Programa

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.generador_datos import GeneradorDatos
from models.sistema import SistemaPrediccionDesercion

def mostrar_menu():
    print("\n" + "="*60)
    print("SISTEMA DE PREDICCIÓN DE DESERCIÓN UNIVERSITARIA")
    print("="*60)
    print("1. Generar datos y entrenar sistema")
    print("2. Mostrar estadísticas generales")
    print("3. Predecir estudiante individual (por ID)")
    print("4. Mostrar TODOS los estudiantes en riesgo")
    print("5. Mostrar TOP 10 estudiantes en riesgo")
    print("6. Salir")
    print("="*60)

def mostrar_estadisticas(sistema, estudiantes):
    """Muestra estadísticas generales"""
    total = len(estudiantes)
    desertores = sum(1 for e in estudiantes if e.deserto)
    
    print("\n" + "="*60)
    print("ESTADÍSTICAS GENERALES (Escala 0-20)")
    print("="*60)
    print(f"Total estudiantes: {total}")
    print(f"Desertores reales: {desertores} ({desertores/total*100:.1f}%)")
    print(f"No desertores: {total - desertores}")
    
    notas = [e.promedio_primer_semestre for e in estudiantes]
    print(f"\n📊 Promedio general: {sum(notas)/len(notas):.1f}/20")
    print(f"   Nota mínima: {min(notas):.1f}/20")
    print(f"   Nota máxima: {max(notas):.1f}/20")
    
    # Deserción por rango de notas
    print("\n📊 Deserción por rango de notas:")
    rangos = [(0, 8), (8, 10), (10, 12), (12, 14), (14, 20)]
    for bajo, alto in rangos:
        grupo = [e for e in estudiantes if bajo <= e.promedio_primer_semestre < alto]
        if grupo:
            des = sum(1 for e in grupo if e.deserto)
            print(f"   {bajo}-{alto}: {des}/{len(grupo)} ({des/len(grupo)*100:.1f}% desertan)")

def predecir_estudiante(sistema, estudiantes):
    """Predice un estudiante individual por ID"""
    try:
        id_buscar = int(input("\nIngrese el ID del estudiante: "))
        estudiante = None
        for e in estudiantes:
            if e.id == id_buscar:
                estudiante = e
                break
        
        if estudiante is None:
            print(f"❌ No se encontró estudiante con ID {id_buscar}")
            return
        
        print("\n" + "-"*40)
        print(f"ESTUDIANTE ID: {estudiante.id}")
        print("-"*40)
        print(f"📊 Promedio: {estudiante.promedio_primer_semestre}/20")
        print(f"📚 Materias reprobadas: {estudiante.materias_reprobadas}")
        print(f"📅 Asistencia: {estudiante.asistencia_promedio}%")
        print(f"💼 Trabaja: {'Sí' if estudiante.trabaja else 'No'} ({estudiante.horas_trabajo}h)" if estudiante.trabaja else "💼 No trabaja")
        print(f"📐 Reprobó Matemáticas: {'Sí' if estudiante.reprobo_matematicas_I else 'No'}")
        print(f"🧪 Reprobó Química: {'Sí' if estudiante.reprobo_quimica_I else 'No'}")
        print(f"📖 Realidad: {'DESERTÓ' if estudiante.deserto else 'NO DESERTÓ'}")
        
        # Predicción del sistema
        prediccion = sistema.predecir(estudiante)
        print(f"\n🔮 PREDICCIÓN DEL SISTEMA:")
        if prediccion['deserta']:
            print(f"   ⚠️ RIESGO ALTO DE DESERCIÓN")
        else:
            print(f"   ✅ RIESGO BAJO DE DESERCIÓN")
        
        # Mostrar factores de riesgo
        alerta = sistema.generar_alerta(estudiante)
        if alerta and alerta.get('factores'):
            print(f"\n📋 Factores de riesgo:")
            for factor in alerta['factores'][:3]:
                print(f"   • {factor}")
        
        # Mostrar recomendaciones
        if alerta and alerta.get('recomendaciones'):
            print(f"\n💡 Recomendaciones:")
            for rec in alerta['recomendaciones'][:2]:
                print(f"   • {rec}")
                
    except ValueError:
        print("❌ Ingrese un ID válido (número)")

def mostrar_todos_riesgo(sistema, estudiantes):
    """Muestra TODOS los estudiantes en riesgo (sin límite)"""
    alertas = sistema.generar_reporte(estudiantes, top_n=None)
    
    if not alertas:
        print("\n✅ No hay estudiantes en riesgo.")
        return
    
    print("\n" + "="*60)
    print(f"⚠️ LISTA COMPLETA DE ESTUDIANTES EN RIESGO ({len(alertas)} total)")
    print("="*60)
    
    for i, alerta in enumerate(alertas, 1):
        print(f"\n{i}. ID: {alerta['estudiante_id']} | Nota: {alerta['nota_promedio']}/20 | Riesgo: {alerta['riesgo']}")
        if alerta.get('factores'):
            print(f"   Factores: {', '.join(alerta['factores'][:2])}")
        if alerta.get('recomendaciones'):
            print(f"   💡 {alerta['recomendaciones'][0]}")
        print("-"*40)

def mostrar_top10_riesgo(sistema, estudiantes):
    """Muestra SOLO los 10 estudiantes con mayor riesgo"""
    alertas = sistema.generar_reporte(estudiantes, top_n=10)
    
    if not alertas:
        print("\n✅ No hay estudiantes en riesgo.")
        return
    
    print("\n" + "="*60)
    print("⚠️ TOP 10 ESTUDIANTES CON MAYOR RIESGO")
    print("="*60)
    
    for i, alerta in enumerate(alertas, 1):
        print(f"\n{i}. ID: {alerta['estudiante_id']} | Nota: {alerta['nota_promedio']}/20 | Riesgo: {alerta['riesgo']}")
        if alerta.get('factores'):
            print(f"   Factores: {', '.join(alerta['factores'][:2])}")
        if alerta.get('recomendaciones'):
            print(f"   💡 {alerta['recomendaciones'][0]}")
        print("-"*40)

def main():
    sistema = None
    estudiantes = None
    generador = GeneradorDatos(seed=42)
    
    while True:
        mostrar_menu()
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            print("\n🔄 Generando datos sintéticos...")
            estudiantes = generador.generar_dataset(n=500)
            print(f"✅ Generados {len(estudiantes)} estudiantes")
            
            sistema = SistemaPrediccionDesercion()
            sistema.entrenar(estudiantes)
            
        elif opcion == "2":
            if sistema is None or estudiantes is None:
                print("\n⚠️ Primero debe entrenar el sistema (opción 1)")
            else:
                mostrar_estadisticas(sistema, estudiantes)
                
        elif opcion == "3":
            if sistema is None or estudiantes is None:
                print("\n⚠️ Primero debe entrenar el sistema (opción 1)")
            else:
                predecir_estudiante(sistema, estudiantes)
                
        elif opcion == "4":
            if sistema is None or estudiantes is None:
                print("\n⚠️ Primero debe entrenar el sistema (opción 1)")
            else:
                mostrar_todos_riesgo(sistema, estudiantes)
                
        elif opcion == "5":
            if sistema is None or estudiantes is None:
                print("\n⚠️ Primero debe entrenar el sistema (opción 1)")
            else:
                mostrar_top10_riesgo(sistema, estudiantes)
                
        elif opcion == "6":
            print("\n👋 Saliendo del sistema...")
            break
            
        else:
            print("\n⚠️ Opción no válida. Intente de nuevo.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()