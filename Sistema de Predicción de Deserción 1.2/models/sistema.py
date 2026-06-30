# models/sistema.py
from models.arbol_decision import ArbolDecisionID3
from models.apriori import Apriori
from models.preprocesador import Preprocesador

class SistemaPrediccionDesercion:
    def __init__(self):
        self.arbol = ArbolDecisionID3()
        self.apriori = Apriori(soporte_minimo=0.03, confianza_minima=0.5)
        self.preprocesador = Preprocesador()
        print("✅ Sistema inicializado (modo genérico)")

    def entrenar(self, estudiantes):
        print("\n" + "="*60)
        print("ENTRENANDO SISTEMA (MODO GENÉRICO)")
        print("ESCALA DE NOTAS: 0 a 20 (aprueba con 10)")
        print("="*60)
        print("1. Preprocesando datos...")
        estudiantes_proc = self.preprocesador.preparar_para_arbol(estudiantes)
        
        atributos = [
            'estrato', 'promedio_categoria', 'asistencia_categoria',
            'materias_categoria', 'materias_reprobadas',
            'trabaja', 'carga_alta', 'bajo_rendimiento_inicial'
        ]
        
        print("2. Entrenando árbol de decisión ID3...")
        self.arbol.entrenar(estudiantes_proc, atributos, max_profundidad=5)
        
        print("3. Preparando transacciones para Apriori...")
        transacciones = self.preprocesador.preparar_para_apriori(estudiantes_proc)
        
        print("4. Generando reglas de asociación con Apriori...")
        self.apriori.generar_reglas(transacciones)
        
        print("\n✅ SISTEMA ENTRENADO CORRECTAMENTE")
        print(f"   Árbol: {self._contar_nodos(self.arbol.raiz)} nodos")
        print(f"   Reglas Apriori: {len(self.apriori.reglas)} encontradas")

    def _contar_nodos(self, nodo):
        if nodo is None:
            return 0
        if nodo.es_hoja():
            return 1
        return 1 + sum(self._contar_nodos(h) for h in nodo.hijos.values())

    def predecir(self, estudiante):
        # Discretizaciones
        if estudiante.promedio_categoria is None:
            estudiante.promedio_categoria = self.preprocesador.discretizar(
                estudiante.promedio_primer_semestre, 'promedio',
                self.preprocesador.cortes.get('promedio', [10, 14]))
        if estudiante.asistencia_categoria is None:
            estudiante.asistencia_categoria = self.preprocesador.discretizar(
                estudiante.asistencia_promedio, 'asistencia',
                self.preprocesador.cortes.get('asistencia', [70, 85]))
        if estudiante.materias_categoria is None:
            estudiante.materias_categoria = self.preprocesador.discretizar(
                estudiante.materias_reprobadas, 'materias',
                self.preprocesador.cortes.get('materias', [1, 3]))

        arbol_predice = self.arbol.predecir(estudiante)
        
        # Reglas lógicas más sensibles
        riesgo_alto = False
        
        if estudiante.materias_reprobadas >= 1:
            riesgo_alto = True
        if estudiante.baja_asistencia:
            riesgo_alto = True
        if estudiante.asistencia_promedio < 85 and estudiante.materias_reprobadas >= 1:
            riesgo_alto = True
        if estudiante.trabaja and estudiante.materias_reprobadas >= 1:
            riesgo_alto = True
        if estudiante.carga_alta:
            riesgo_alto = True
        if estudiante.promedio_primer_semestre < 10:
            riesgo_alto = True
        if not estudiante.tutorias_asistio and estudiante.materias_reprobadas >= 1:
            riesgo_alto = True
        if estudiante.rezago_academico:
            riesgo_alto = True
        
        deserta = arbol_predice or riesgo_alto
        return {'deserta': deserta, 'riesgo': 'ALTO' if deserta else 'BAJO'}

    def generar_alerta(self, estudiante):
        pred = self.predecir(estudiante)
        if not pred['deserta']:
            return None
        recomendaciones = []
        if hasattr(estudiante, 'notas') and estudiante.notas:
            for mat, nota in estudiante.notas.items():
                if nota < 10:
                    recomendaciones.append(f"📖 Tutoría de {mat} (nota {nota}/20)")
        if estudiante.bajo_rendimiento_inicial:
            recomendaciones.append(f"📚 Curso de nivelación (promedio: {estudiante.promedio_primer_semestre}/20)")
        if estudiante.trabaja and estudiante.horas_trabajo > 20:
            recomendaciones.append("💼 Evaluar beca o reducción de carga laboral")
        if estudiante.asistencia_promedio < 70:
            recomendaciones.append(f"📅 Mejorar asistencia ({estudiante.asistencia_promedio}%)")
        if not estudiante.tutorias_asistio:
            recomendaciones.append("🎓 Asistir a tutorías disponibles")
        if estudiante.rezago_academico:
            recomendaciones.append(f"📖 Reducir carga académica ({estudiante.materias_reprobadas} materias reprobadas)")
        if estudiante.carga_alta:
            recomendaciones.append("⚖️ Apoyo para conciliar estudio y trabajo/familia")
        return {
            'estudiante_id': estudiante.id,
            'riesgo': pred['riesgo'],
            'nota_promedio': estudiante.promedio_primer_semestre,
            'factores': self._identificar_factores(estudiante),
            'recomendaciones': recomendaciones
        }

    def _identificar_factores(self, estudiante):
        factores = []
        if estudiante.bajo_rendimiento_inicial:
            factores.append(f"🔴 Nota CRÍTICA: {estudiante.promedio_primer_semestre}/20 (reprobado)")
        elif estudiante.promedio_primer_semestre < 12:
            factores.append(f"🟡 Nota baja: {estudiante.promedio_primer_semestre}/20 (cerca del mínimo)")
        elif estudiante.promedio_primer_semestre < 14:
            factores.append(f"🟢 Nota media: {estudiante.promedio_primer_semestre}/20 (requiere seguimiento)")
        
        reprobadas = []
        if hasattr(estudiante, 'notas') and estudiante.notas:
            for mat, nota in estudiante.notas.items():
                if nota < 10:
                    reprobadas.append(f"{mat} ({nota}/20)")
        if reprobadas:
            factores.append(f"📚 Materias reprobadas: {', '.join(reprobadas)}")
        elif estudiante.materias_reprobadas > 0:
            factores.append(f"📚 {estudiante.materias_reprobadas} materia(s) reprobada(s)")
        
        if estudiante.baja_asistencia:
            factores.append(f"⚠️ Baja asistencia: {estudiante.asistencia_promedio}%")
        elif estudiante.asistencia_promedio < 85:
            factores.append(f"📅 Asistencia mejorable: {estudiante.asistencia_promedio}%")
        
        if estudiante.trabaja:
            if estudiante.horas_trabajo > 30:
                factores.append(f"💼 Trabajo tiempo completo: {estudiante.horas_trabajo}h")
            elif estudiante.horas_trabajo > 20:
                factores.append(f"💼 Carga laboral alta: {estudiante.horas_trabajo}h")
            else:
                factores.append(f"💼 Trabaja {estudiante.horas_trabajo}h")
        if estudiante.hijos:
            factores.append("👶 Tiene hijos")
        if estudiante.carga_alta:
            factores.append("⚖️ Carga alta (trabajo >20h o hijos)")
        if not estudiante.tutorias_asistio and (reprobadas or estudiante.promedio_primer_semestre < 12):
            factores.append("🎓 No ha utilizado tutorías disponibles")
        if not factores:
            factores.append("✅ Sin factores de riesgo detectados")
        return factores

    def generar_reporte(self, estudiantes, top_n=None):
        alertas = []
        for e in estudiantes:
            a = self.generar_alerta(e)
            if a:
                alertas.append(a)
        alertas.sort(key=lambda x: x.get('nota_promedio', 20))
        return alertas if top_n is None else alertas[:top_n]

    def diagnosticar_estudiante(self, estudiante):
        if estudiante.promedio_categoria is None:
            estudiante.promedio_categoria = self.preprocesador.discretizar(
                estudiante.promedio_primer_semestre, 'promedio',
                self.preprocesador.cortes.get('promedio', [10, 14]))
        if estudiante.asistencia_categoria is None:
            estudiante.asistencia_categoria = self.preprocesador.discretizar(
                estudiante.asistencia_promedio, 'asistencia',
                self.preprocesador.cortes.get('asistencia', [70, 85]))
        if estudiante.materias_categoria is None:
            estudiante.materias_categoria = self.preprocesador.discretizar(
                estudiante.materias_reprobadas, 'materias',
                self.preprocesador.cortes.get('materias', [1, 3]))
        # Usar la predicción completa del sistema (árbol + reglas lógicas)
        pred = self.predecir(estudiante)
        return {
            'id': estudiante.id,
            'nota_real': estudiante.promedio_primer_semestre,
            'nota_categoria': estudiante.promedio_categoria,
            'asistencia_categoria': estudiante.asistencia_categoria,
            'materias_categoria': estudiante.materias_categoria,
            'materias_reprobadas': estudiante.materias_reprobadas,
            'trabaja': estudiante.trabaja,
            'horas_trabajo': estudiante.horas_trabajo,
            'carga_alta': estudiante.carga_alta,
            'bajo_rendimiento': estudiante.bajo_rendimiento_inicial,
            'rezago_academico': estudiante.rezago_academico,
            'baja_asistencia': estudiante.baja_asistencia,
            'factores': self._identificar_factores(estudiante),
            'prediccion': pred['riesgo']
        }

    # Métodos adicionales para consola (opcionales, para compatibilidad)
    def mostrar_estadisticas(self, estudiantes):
        total = len(estudiantes)
        desertores = sum(1 for e in estudiantes if e.deserto)
        print("\n" + "="*60)
        print("ESTADÍSTICAS GENERALES")
        print("="*60)
        print(f"Total: {total}")
        print(f"Desertores: {desertores} ({desertores/total*100:.1f}%)")
        notas = [e.promedio_primer_semestre for e in estudiantes]
        if notas:
            print(f"Promedio general: {sum(notas)/len(notas):.1f}/20")
            print(f"Mínima: {min(notas):.1f} | Máxima: {max(notas):.1f}")

    def mostrar_reglas(self, max_reglas=10):
        reglas = self.apriori.obtener_reglas_desercion()
        print("\n" + "="*60)
        print("REGLAS DE ASOCIACIÓN")
        print("="*60)
        if not reglas:
            print("No se encontraron reglas.")
            return
        for i, r in enumerate(reglas[:max_reglas], 1):
            ant = " Y ".join(sorted(r['antecedente']))
            print(f"{i}. SI [{ant}] → deserto (confianza {r['confianza']*100:.1f}%)")

    def mostrar_arbol(self):
        print("\n" + "="*60)
        print("ÁRBOL DE DECISIÓN")
        print("="*60)
        self.arbol.imprimir()