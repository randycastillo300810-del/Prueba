# models/generador_datos.py
# Versión realista: notas distribuidas normalmente, deserción ~15-25%

import random

class GeneradorDatos:
    def __init__(self, seed=42):
        random.seed(seed)
    
    def generar_estudiante(self, id):
        # ============================================================
        # 1. NOTA: distribución normal con media 12.5 y desviación 2.8
        #    Así la mayoría (aprox 70%) estará entre 9.7 y 15.3
        # ============================================================
        promedio = random.gauss(12.5, 2.8)
        promedio = max(0, min(20, round(promedio, 1)))
        
        # ============================================================
        # 2. DESERCIÓN: probabilidad realista basada en la nota
        #    Tasa global de deserción será ~20-25%
        # ============================================================
        if promedio >= 14:
            prob_desercion = 0.03   # 3% (notas muy altas)
        elif promedio >= 12:
            prob_desercion = 0.08   # 8%
        elif promedio >= 10:
            prob_desercion = 0.18   # 18%
        elif promedio >= 8:
            prob_desercion = 0.35   # 35%
        else:
            prob_desercion = 0.60   # 60% (notas muy bajas, pocos estudiantes)
        
        deserto = random.random() < prob_desercion
        
        # ============================================================
        # 3. MATERIAS REPROBADAS (coherentes con la nota)
        # ============================================================
        if promedio < 8:
            materias_reprobadas = random.randint(3, 5)
        elif promedio < 10:
            materias_reprobadas = random.randint(1, 3)
        elif promedio < 12:
            materias_reprobadas = random.randint(0, 2)
        elif promedio < 14:
            materias_reprobadas = random.randint(0, 1)
        else:
            materias_reprobadas = 0
        #CODIGO DE RANDY CASTILLO 30727559
        # ============================================================
        # 4. MATERIAS CRÍTICAS (Matemáticas y Química)
        # ============================================================
        reprobo_mate = random.random() < (0.35 if promedio < 10 else 0.08)
        reprobo_quimica = random.random() < (0.30 if promedio < 10 else 0.06)
        
        # ============================================================
        # 5. ASISTENCIA (relacionada con la nota)
        # ============================================================
        asistencia_base = 85 - (12.5 - promedio) * 1.2
        asistencia_base = max(55, min(98, asistencia_base))
        asistencia = round(random.gauss(asistencia_base, 8), 1)
        asistencia = max(0, min(100, asistencia))
        
        # ============================================================
        # 6. TRABAJO (más probable en notas medias-bajas)
        # ============================================================
        if promedio < 10:
            prob_trabajo = 0.35
        elif promedio < 13:
            prob_trabajo = 0.25
        else:
            prob_trabajo = 0.12
        trabaja = random.random() < prob_trabajo
        horas_trabajo = random.choice([15, 20, 25, 30]) if trabaja else 0
        
        # ============================================================
        # 7. TUTORÍAS (más probable si reprobó alguna materia crítica)
        # ============================================================
        tutorias = reprobo_mate or reprobo_quimica
        
        # ============================================================
        # 8. DATOS DEMOGRÁFICOS (sin sesgo extremo)
        # ============================================================
        estrato = random.choices([1,2,3,4,5,6], weights=[0.15,0.20,0.30,0.20,0.10,0.05])[0]
        
        datos = {
            'edad': random.randint(17, 30),
            'genero': random.choice(['M', 'F']),
            'estrato': estrato,
            'foraneo': random.random() < 0.25,
            'trabaja': trabaja,
            'horas_trabajo': horas_trabajo,
            'hijos': random.random() < 0.04,
            'educacion_padres': random.choices([0,1,2], weights=[0.25,0.45,0.30])[0],
            'promedio_primer_semestre': promedio,
            'promedio_acumulado': round(promedio * random.uniform(0.96, 1.04), 1),
            'materias_reprobadas': materias_reprobadas,
            'materias_retiradas': random.randint(0,1) if promedio < 10 else 0,
            'reprobo_matematicas_I': reprobo_mate,
            'reprobo_quimica_I': reprobo_quimica,
            'asistencia_promedio': asistencia,
            'tutorias_asistio': tutorias,
            'deserto': deserto
        }
        
        from models.estudiante import Estudiante
        return Estudiante(id, datos)
    
    def generar_dataset(self, n=500):
        estudiantes = []
        for i in range(n):
            estudiantes.append(self.generar_estudiante(i))
        return estudiantes