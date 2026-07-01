# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.utils import platform
import sys
import os

# Añadir modelos al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models.sistema import SistemaPrediccionDesercion
from models.estudiante import Estudiante
from models.lector_excel import LectorExcel

# Colores
COLORS = {
    'primary': (0.118, 0.533, 0.898, 1),
    'danger': (0.898, 0.224, 0.208, 1),
    'success': (0.263, 0.627, 0.278, 1),
    'warning': (0.984, 0.549, 0, 1),
    'bg': (0.059, 0.059, 0.102, 1),
    'card': (0.086, 0.125, 0.243, 1),
    'sidebar': (0.102, 0.102, 0.180, 1),
}

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sistema = None
        self.estudiantes = None
        
        # Layout principal
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=0.08, padding=[10,5])
        with header.canvas.before:
            Color(*COLORS['sidebar'])
            Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i, p: setattr(i, 'canvas.before.children[1].pos', p))
        
        title = Label(text="🎓 Predicción de Deserción Universitaria", 
                     bold=True, font_size='16sp', color=(1,1,1,1))
        header.add_widget(title)
        main_layout.add_widget(header)
        
        # Contenido principal con Scroll
        scroll = ScrollView()
        self.content = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # Botones de acción
        btn_cargar = Button(text="📂 Cargar Archivo Excel", 
                          size_hint_y=None, height=dp(50),
                          background_color=COLORS['primary'])
        btn_cargar.bind(on_press=self.cargar_excel)
        self.content.add_widget(btn_cargar)
        
        btn_dashboard = Button(text="📊 Dashboard Estadísticas",
                             size_hint_y=None, height=dp(50),
                             background_color=COLORS['primary'])
        btn_dashboard.bind(on_press=self.mostrar_dashboard)
        self.content.add_widget(btn_dashboard)
        
        btn_riesgo = Button(text="⚠️ Lista de Estudiantes en Riesgo",
                          size_hint_y=None, height=dp(50),
                          background_color=COLORS['danger'])
        btn_riesgo.bind(on_press=self.lista_riesgo)
        self.content.add_widget(btn_riesgo)
        
        # Búsqueda
        search_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
        self.search_input = TextInput(hint_text="Buscar por nombre o cédula...", multiline=False)
        search_box.add_widget(self.search_input)
        btn_buscar = Button(text="🔍 Buscar", size_hint_x=0.3, background_color=COLORS['warning'])
        btn_buscar.bind(on_press=self.buscar_estudiante)
        search_box.add_widget(btn_buscar)
        self.content.add_widget(search_box)
        
        # Diagnóstico individual
        diag_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=10)
        self.id_input = TextInput(hint_text="Ingrese ID del estudiante...", multiline=False, input_filter='int')
        diag_box.add_widget(self.id_input)
        btn_diag = Button(text="🔍 Diagnosticar", size_hint_x=0.3, background_color=COLORS['warning'])
        btn_diag.bind(on_press=self.diagnosticar_individual)
        diag_box.add_widget(btn_diag)
        self.content.add_widget(diag_box)
        
        # Área de resultados
        self.result_label = Label(text="", markup=True, size_hint_y=None, halign='left', valign='top')
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.content.add_widget(self.result_label)
        
        # Status
        self.status = Label(text="💡 Sistema inactivo. Cargue un archivo Excel para comenzar.",
                          size_hint_y=None, height=dp(30), color=(1,0.7,0,1))
        self.content.add_widget(self.status)
        
        scroll.add_widget(self.content)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def cargar_excel(self, instance):
        """Carga archivo Excel usando filechooser"""
        from plyer import filechooser
        filechooser.open_file(on_selection=self.procesar_excel, 
                             filters=[("Excel", "*.xlsx")])
    
    def procesar_excel(self, selection):
        if not selection:
            return
        
        archivo = selection[0]
        try:
            lector = LectorExcel()
            lector.cargar_datos(archivo)
            self.estudiantes = lector.convertir_a_estudiantes()
            
            if not self.estudiantes:
                self.result_label.text = "❌ No se pudieron cargar estudiantes."
                return
            
            self.sistema = SistemaPrediccionDesercion()
            self.sistema.entrenar(self.estudiantes)
            
            total = len(self.estudiantes)
            riesgo = sum(1 for e in self.estudiantes if self.sistema.predecir(e)['deserta'])
            
            self.status.text = f"✅ {total} estudiantes cargados | {riesgo} en riesgo"
            self.status.color = (0.5,1,0.5,1)
            self.result_label.text = f"✅ Archivo cargado exitosamente\n📊 {total} estudiantes procesados"
            
        except PermissionError:
            self.result_label.text = "❌ Error: Cierre el archivo en Excel e intente de nuevo."
        except Exception as e:
            self.result_label.text = f"❌ Error: {str(e)}"
    
    def mostrar_dashboard(self, instance):
        if not self.sistema:
            self.result_label.text = "⚠️ Primero cargue un archivo Excel."
            return
        
        total = len(self.estudiantes)
        riesgo = sum(1 for e in self.estudiantes if self.sistema.predecir(e)['deserta'])
        seguro = total - riesgo
        tasa = (riesgo/total)*100 if total > 0 else 0
        notas = [e.promedio_primer_semestre for e in self.estudiantes]
        prom = sum(notas)/len(notas) if notas else 0
        
        texto = f"""
        [b][size=20]📊 DASHBOARD DE ESTADÍSTICAS[/size][/b]
        
        [b]👥 Total estudiantes:[/b] {total}
        [b]⚠️ En riesgo:[/b] {riesgo} ({tasa:.1f}%)
        [b]✅ Seguros:[/b] {seguro} ({100-tasa:.1f}%)
        [b]📝 Promedio global:[/b] {prom:.1f}/20
        [b]📉 Nota mínima:[/b] {min(notas):.1f}/20
        [b]📈 Nota máxima:[/b] {max(notas):.1f}/20
        
        [b][size=16]📊 ANÁLISIS POR RANGO DE NOTAS:[/size][/b]
        """
        
        rangos = [(0,8,"0-8"), (8,10,"8-10"), (10,12,"10-12"), (12,14,"12-14"), (14,21,"14-20")]
        for bajo, alto, etiqueta in rangos:
            grupo = [e for e in self.estudiantes if bajo <= e.promedio_primer_semestre < alto]
            if grupo:
                r = sum(1 for e in grupo if self.sistema.predecir(e)['deserta'])
                texto += f"  {etiqueta}: {r}/{len(grupo)} en riesgo ({r/len(grupo)*100:.1f}%)\n"
        
        self.result_label.text = texto
    
    def lista_riesgo(self, instance):
        if not self.sistema:
            self.result_label.text = "⚠️ Primero cargue un archivo Excel."
            return
        
        riesgo_lista = []
        for e in self.estudiantes:
            pred = self.sistema.predecir(e)
            if pred['deserta']:
                riesgo_lista.append((e, pred))
        
        if not riesgo_lista:
            self.result_label.text = "✅ No hay estudiantes en riesgo."
            return
        
        riesgo_lista.sort(key=lambda x: x[0].promedio_primer_semestre)
        
        texto = f"[b][size=20]⚠️ ESTUDIANTES EN RIESGO ({len(riesgo_lista)})[/size][/b]\n\n"
        
        for i, (e, pred) in enumerate(riesgo_lista[:30], 1):
            nombre = getattr(e, 'nombre_completo', '') or f"ID {e.id}"
            texto += f"[b]{i}. {nombre}[/b]\n"
            texto += f"   ID: {e.id} | Nota: {e.promedio_primer_semestre}/20 | Riesgo: {pred['riesgo']}\n"
            
            if e.materias_reprobadas >= 2:
                texto += f"   ⚠️ {e.materias_reprobadas} materias reprobadas\n"
            if e.baja_asistencia:
                texto += f"   ⚠️ Baja asistencia: {e.asistencia_promedio}%\n"
            texto += "─"*40 + "\n"
        
        if len(riesgo_lista) > 30:
            texto += f"\n... y {len(riesgo_lista)-30} más"
        
        self.result_label.text = texto
    
    def buscar_estudiante(self, instance):
        if not self.sistema:
            self.result_label.text = "⚠️ Primero cargue un archivo Excel."
            return
        
        texto_buscar = self.search_input.text.strip().lower()
        if not texto_buscar:
            self.result_label.text = "⚠️ Ingrese nombre o cédula para buscar."
            return
        
        resultados = []
        for e in self.estudiantes:
            nombre = (getattr(e, 'nombre_completo', '') or '').lower()
            cedula = str(getattr(e, 'cedula', '')).lower()
            if texto_buscar in nombre or texto_buscar in cedula:
                resultados.append(e)
        
        if not resultados:
            self.result_label.text = f"❌ No se encontró: '{self.search_input.text}'"
            return
        
        texto = f"[b]🔍 Resultados para: '{self.search_input.text}' ({len(resultados)})[/b]\n\n"
        
        for e in resultados:
            nombre = getattr(e, 'nombre_completo', '') or f"ID {e.id}"
            pred = self.sistema.predecir(e)
            emoji = "⚠️" if pred['deserta'] else "✅"
            texto += f"{emoji} {nombre} | ID: {e.id} | Nota: {e.promedio_primer_semestre}/20\n"
        
        self.result_label.text = texto
    
    def diagnosticar_individual(self, instance):
        if not self.sistema:
            self.result_label.text = "⚠️ Primero cargue un archivo Excel."
            return
        
        try:
            id_int = int(self.id_input.text)
            estudiante = next((e for e in self.estudiantes if e.id == id_int), None)
            
            if not estudiante:
                self.result_label.text = f"❌ Estudiante ID {id_int} no encontrado."
                return
            
            nombre = getattr(estudiante, 'nombre_completo', '') or f"Estudiante {estudiante.id}"
            pred = self.sistema.predecir(estudiante)
            diag = self.sistema.diagnosticar_estudiante(estudiante)
            alerta = self.sistema.generar_alerta(estudiante)
            
            riesgo_emoji = "⚠️" if pred['deserta'] else "✅"
            
            texto = f"""
            [b][size=22]{nombre}[/size][/b]
            [b][size=18]{riesgo_emoji} {pred['riesgo']} RIESGO[/size][/b]
            
            [b]📊 DATOS ACADÉMICOS:[/b]
            • Promedio: {estudiante.promedio_primer_semestre}/20
            • Asistencia: {estudiante.asistencia_promedio}%
            • Materias reprobadas: {estudiante.materias_reprobadas}
            
            [b]⚠️ FACTORES DE RIESGO:[/b]
            """
            
            for factor in diag.get('factores', []):
                texto += f"• {factor}\n"
            
            if alerta and alerta.get('recomendaciones'):
                texto += f"\n[b]💡 RECOMENDACIONES:[/b]\n"
                for rec in alerta['recomendaciones']:
                    texto += f"• {rec}\n"
            
            # Notas por materia
            if hasattr(estudiante, 'notas') and estudiante.notas:
                texto += f"\n[b]📚 NOTAS POR MATERIA:[/b]\n"
                for mat, nota in estudiante.notas.items():
                    emoji = "🔴" if nota < 10 else ("🟡" if nota < 14 else "🟢")
                    texto += f"{emoji} {mat}: {nota}/20\n"
            
            self.result_label.text = texto
            
        except ValueError:
            self.result_label.text = "❌ El ID debe ser un número entero."


class DesercionApp(App):
    def build(self):
        self.title = "Predicción de Deserción"
        return MainScreen()

if __name__ == '__main__':
    DesercionApp().run()
