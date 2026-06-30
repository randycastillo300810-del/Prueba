import pandas as pd
from models.estudiante import Estudiante

class LectorExcel:
    def __init__(self):
        self.df = None

    def cargar_datos(self, ruta_archivo):
        self.df = pd.read_excel(ruta_archivo)
        return self.df

    def convertir_a_estudiantes(self):
        if self.df is None or self.df.empty:
            return []

        # Columnas que no son materias (ajústalas según tu Excel)
        columnas_no_materias = [
            'Cédula', 'Nombres', 'Apellidos', 'Turno', 'Sección',
            'Promedio Final', 'Carrera', 'Asistencia', 'Trabaja',
            'Horas_Trabajo', 'Hijos', 'Estrato', 'Tutorias', 'Carga_Alta',
            'deserto', 'ID', 'id', 'Edad', 'Género', 'Foráneo', 'Educación_Padres'
        ]

        # Detectar columnas de materias (numéricas y no excluidas)
        columnas_materias = [
            col for col in self.df.columns
            if col not in columnas_no_materias and pd.api.types.is_numeric_dtype(self.df[col])
        ]

        print(f"📚 Materias detectadas: {columnas_materias}")

        estudiantes = []
        for idx, row in self.df.iterrows():
            notas = {}
            for materia in columnas_materias:
                nota = row.get(materia)
                if pd.notna(nota):
                    notas[materia] = float(nota)

            # Promedio
            if 'Promedio Final' in self.df.columns and pd.notna(row['Promedio Final']):
                promedio = float(row['Promedio Final'])
            else:
                promedio = sum(notas.values()) / len(notas) if notas else 10.0

            materias_reprobadas = sum(1 for nota in notas.values() if nota < 10)

            def get_val(col, default):
                val = row.get(col)
                return default if pd.isna(val) else val

            datos = {
                'id': idx,
                'edad': get_val('Edad', 20),
                'genero': get_val('Género', 'M'),
                'estrato': get_val('Estrato', 3),
                'foraneo': get_val('Foráneo', False),
                'trabaja': get_val('Trabaja', False),
                'horas_trabajo': get_val('Horas_Trabajo', 0),
                'hijos': get_val('Hijos', False),
                'educacion_padres': get_val('Educación_Padres', 1),
                'promedio_primer_semestre': round(promedio, 2),
                'promedio_acumulado': round(promedio, 2),
                'materias_reprobadas': materias_reprobadas,
                'materias_retiradas': get_val('Materias_Retiradas', 0),
                'asistencia_promedio': get_val('Asistencia', 85.0),
                'tutorias_asistio': get_val('Tutorias', False),
                'deserto': get_val('deserto', False)
            }

            estudiante = Estudiante(idx, datos)
            estudiante.notas = notas

            # Datos personales
            estudiante.nombre_completo = f"{get_val('Nombres', '')} {get_val('Apellidos', '')}".strip()
            estudiante.cedula = get_val('Cédula', '')
            estudiante.carrera = get_val('Carrera', '')
            estudiante.turno = get_val('Turno', '')
            estudiante.seccion = get_val('Sección', '')

            estudiantes.append(estudiante)

        return estudiantes