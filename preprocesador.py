# models/preprocesador.py
class Preprocesador:
    def __init__(self):
        self.cortes = {}

    def discretizar(self, valores, nombre_variable, num_bins=3):
        if not valores:
            return []
        if isinstance(valores, (int, float)):
            valores = [valores]
        # Calcular cortes por percentiles si hay suficientes datos
        if len(valores) > 10:
            valores_ordenados = sorted(valores)
            n = len(valores_ordenados)
            cortes = [valores_ordenados[int(n * i / num_bins)] for i in range(1, num_bins)]
        else:
            # Valores por defecto
            if nombre_variable == 'promedio':
                cortes = [10, 14]
            elif nombre_variable == 'asistencia':
                cortes = [70, 85]
            elif nombre_variable == 'materias':
                cortes = [1, 3]
            else:
                cortes = [0, 0]
        self.cortes[nombre_variable] = cortes
        # Clasificar
        categorias = []
        for v in valores:
            if v < cortes[0]:
                categorias.append('bajo')
            elif v < cortes[1]:
                categorias.append('medio')
            else:
                categorias.append('alto')
        return categorias

    def preparar_para_arbol(self, estudiantes):
        promedios = [e.promedio_primer_semestre for e in estudiantes]
        asistencias = [e.asistencia_promedio for e in estudiantes]
        materias = [e.materias_reprobadas for e in estudiantes]
        self.discretizar(promedios, 'promedio')
        self.discretizar(asistencias, 'asistencia')
        self.discretizar(materias, 'materias')
        for e in estudiantes:
            e.promedio_categoria = self.discretizar([e.promedio_primer_semestre], 'promedio')[0]
            e.asistencia_categoria = self.discretizar([e.asistencia_promedio], 'asistencia')[0]
            e.materias_categoria = self.discretizar([e.materias_reprobadas], 'materias')[0]
        return estudiantes

    def preparar_para_apriori(self, estudiantes):
        transacciones = []
        for e in estudiantes:
            transaccion = set()
            transaccion.add(f"promedio_{e.promedio_categoria}")
            transaccion.add(f"asistencia_{e.asistencia_categoria}")
            transaccion.add(f"materias_{e.materias_categoria}")
            transaccion.add(f"estrato_{e.estrato}")
            if e.trabaja:
                transaccion.add(f"trabaja_{e.horas_trabajo}h")
            if e.bajo_rendimiento_inicial:
                transaccion.add("bajo_rendimiento")
            if e.rezago_academico:
                transaccion.add("rezago_academico")
            if e.carga_alta:
                transaccion.add("carga_alta")
            if e.tutorias_asistio:
                transaccion.add("tutorias")
            if hasattr(e, 'notas') and e.notas:
                for materia, nota in e.notas.items():
                    if nota < 10:
                        transaccion.add(f"REPROBO_{materia}")
            transaccion.add("deserto" if e.deserto else "no_deserto")
            transacciones.append(transaccion)
        return transacciones