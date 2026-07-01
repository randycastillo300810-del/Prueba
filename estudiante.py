class Estudiante:
    def __init__(self, id, datos):
        self.id = id
        self.edad = datos.get('edad', 18)
        self.genero = datos.get('genero', 'M')
        self.estrato = datos.get('estrato', 3)
        self.foraneo = datos.get('foraneo', False)
        self.trabaja = datos.get('trabaja', False)
        self.horas_trabajo = datos.get('horas_trabajo', 0)
        self.hijos = datos.get('hijos', False)
        self.educacion_padres = datos.get('educacion_padres', 1)
        self.promedio_primer_semestre = datos.get('promedio_primer_semestre', 10.0)
        self.promedio_acumulado = datos.get('promedio_acumulado', 10.0)
        self.materias_reprobadas = datos.get('materias_reprobadas', 0)
        self.materias_retiradas = datos.get('materias_retiradas', 0)
        self.asistencia_promedio = datos.get('asistencia_promedio', 85.0)
        self.tutorias_asistio = datos.get('tutorias_asistio', False)
        self.deserto = datos.get('deserto', False)
        
        # Factores compuestos
        self.carga_alta = (self.trabaja and self.horas_trabajo > 20) or self.hijos
        self.rezago_academico = self.materias_reprobadas > 2
        self.bajo_rendimiento_inicial = self.promedio_primer_semestre < 10
        self.baja_asistencia = self.asistencia_promedio < 70
        
        # Discretizaciones (se llenarán después)
        self.promedio_categoria = None
        self.asistencia_categoria = None
        self.materias_categoria = None
        
        # Diccionario de notas (se llena desde el lector)
        self.notas = {}
        
        # Datos personales adicionales (opcional)
        self.nombre_completo = ""
        self.cedula = ""
        self.carrera = ""
        self.turno = ""
        self.seccion = ""
    
    def __repr__(self):
        return f"Estudiante({self.id}, promedio={self.promedio_primer_semestre}, deserto={self.deserto})"