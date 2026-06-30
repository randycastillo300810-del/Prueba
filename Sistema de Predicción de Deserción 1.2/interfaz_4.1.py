import customtkinter as ctk
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
from tkinter import messagebox

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.generador_datos import GeneradorDatos
from models.sistema import SistemaPrediccionDesercion
from models.lector_excel import LectorExcel

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── PALETA DE COLORES ────────────────────────────────────────
COLORS = {
    "primary": "#1E88E5",
    "primary_dark": "#1565C0",
    "success": "#43A047",
    "success_dark": "#2E7D32",
    "danger": "#E53935",
    "danger_dark": "#C62828",
    "warning": "#FB8C00",
    "warning_dark": "#EF6C00",
    "purple": "#8E24AA",
    "purple_dark": "#6A1B9A",
    "teal": "#00897B",
    "teal_dark": "#00695C",
    "sidebar_bg": "#1a1a2e",
    "card_bg": "#16213e",
    "main_bg": "#0f0f1a",
}


class AppMejorada:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sistema de Predicción de Deserción Universitaria")
        self.root.geometry("1400x850")
        self.root.minsize(1200, 750)

        self.sistema = None
        self.estudiantes = None
        self.generador = GeneradorDatos()

        # Variables de estado
        self.modo_sidebar = "datos"  # datos, analisis, diagnostico
        self.estado_sistema = "inactivo"
        self.total_estudiantes = 0
        self.en_riesgo = 0

        self.crear_interfaz()

    # ─── CONSTRUCCIÓN PRINCIPAL ────────────────────────────────
    def crear_interfaz(self):
        # Contenedor principal (sidebar + contenido)
        container = ctk.CTkFrame(self.root, fg_color=COLORS["main_bg"])
        container.pack(fill="both", expand=True)

        # ─── SIDEBAR ───────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(container, width=280, fg_color=COLORS["sidebar_bg"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo / Título en sidebar
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(20, 10))

        ctk.CTkLabel(logo_frame, text="🎓", font=ctk.CTkFont(size=36)).pack()
        ctk.CTkLabel(logo_frame, text="Predicción de\nDeserción", font=ctk.CTkFont(size=18, weight="bold"),
                     justify="center").pack(pady=(5, 0))
        ctk.CTkLabel(logo_frame, text="Universitaria", font=ctk.CTkFont(size=12),
                     text_color="#888888").pack()

        # Separador
        ctk.CTkFrame(self.sidebar, height=2, fg_color="#333355").pack(fill="x", padx=20, pady=10)

        # ─── BOTONES DEL SIDEBAR ─────────────────────────────
        self.seccion_label = ctk.CTkLabel(self.sidebar, text="SECCIÓN DE DATOS",
                                          font=ctk.CTkFont(size=11, weight="bold"),
                                          text_color="#8888AA")
        self.seccion_label.pack(anchor="w", padx=20, pady=(5, 5))

        # Grupo: Datos
        self.btn_generar = self._crear_btn_sidebar(
            "📊  1. Generar Datos Sintéticos",
            self.entrenar, COLORS["success"], COLORS["success_dark"]
        )
        self.btn_cargar = self._crear_btn_sidebar(
            "📁  2. Cargar Excel Real",
            self.cargar_excel, COLORS["teal"], COLORS["teal_dark"]
        )

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#333355").pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.sidebar, text="SECCIÓN DE ANÁLISIS",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      text_color="#8888AA").pack(anchor="w", padx=20, pady=(0, 5))

        # Grupo: Análisis
        self.btn_estadisticas = self._crear_btn_sidebar(
            "📈  3. Dashboard Estadísticas",
            self.mostrar_estadisticas, COLORS["primary"], COLORS["primary_dark"]
        )
        self.btn_riesgo = self._crear_btn_sidebar(
            "⚠️  4. Lista en Riesgo",
            self.lista_completa_riesgo, COLORS["purple"], COLORS["purple_dark"]
        )

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#333355").pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(self.sidebar, text="SECCIÓN DE DIAGNÓSTICO",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      text_color="#8888AA").pack(anchor="w", padx=20, pady=(0, 5))

        # Grupo: Diagnóstico
        self.btn_diagnostico = self._crear_btn_sidebar(
            "🔍  5. Diagnóstico Individual",
            self.diagnostico_individual, COLORS["warning"], COLORS["warning_dark"]
        )

        # Barra de búsqueda en sidebar
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#333355").pack(fill="x", padx=20, pady=10)

        buscar_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        buscar_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(buscar_frame, text="🔎  BÚSQUEDA RÁPIDA",
                      font=ctk.CTkFont(size=11, weight="bold"),
                      text_color="#8888AA").pack(anchor="w")

        self.entry_buscar = ctk.CTkEntry(buscar_frame, placeholder_text="Nombre o Cédula...",
                                          height=38, font=ctk.CTkFont(size=13))
        self.entry_buscar.pack(fill="x", pady=(8, 5))

        btn_buscar = ctk.CTkButton(buscar_frame, text="Buscar y Diagnosticar",
                                    command=self.buscar_y_diagnosticar,
                                    fg_color=COLORS["purple"], hover_color=COLORS["purple_dark"],
                                    height=35, font=ctk.CTkFont(size=12, weight="bold"))
        btn_buscar.pack(fill="x")

        # ─── ÁREA DE CONTENIDO PRINCIPAL ─────────────────────
        self.main_content = ctk.CTkFrame(container, fg_color=COLORS["main_bg"], corner_radius=0)
        self.main_content.pack(side="left", fill="both", expand=True)

        # Header con título y estado
        self._crear_header()

        # Área de pestañas (tab view)
        self._crear_tab_view()

        # Barra de estado inferior
        self._crear_status_bar()

    def _crear_header(self):
        """Header superior con título y KPI cards"""
        header = ctk.CTkFrame(self.main_content, fg_color=COLORS["sidebar_bg"], height=90, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=25)

        ctk.CTkLabel(title_frame, text="Sistema de Predicción de Deserción",
                      font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(12, 0))
        ctk.CTkLabel(title_frame, text="Escala de notas: 0 a 20 (aprueba con 10)",
                      font=ctk.CTkFont(size=12), text_color="#AAAAAA").pack(anchor="w")

        # KPIs en el header
        kpi_frame = ctk.CTkFrame(header, fg_color="transparent")
        kpi_frame.pack(side="right", padx=20, pady=10)

        # KPI: Total estudiantes
        self.kpi_total = self._crear_kpi(kpi_frame, "👥 Total", "0", COLORS["primary"])
        self.kpi_total.pack(side="left", padx=5)

        # KPI: En riesgo
        self.kpi_riesgo = self._crear_kpi(kpi_frame, "⚠️ En Riesgo", "0", COLORS["danger"])
        self.kpi_riesgo.pack(side="left", padx=5)

        # KPI: Estado
        self.kpi_estado = self._crear_kpi(kpi_frame, "💡 Estado", "Inactivo", COLORS["warning"])
        self.kpi_estado.pack(side="left", padx=5)

    def _crear_kpi(self, parent, titulo, valor, color):
        """Crea una tarjeta KPI"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=10, width=140, height=60)
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=10), text_color="#AAAAAA").pack(anchor="w", padx=12, pady=(6, 0))
        self._kpi_label = ctk.CTkLabel(frame, text=valor, font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
        self._kpi_label.pack(anchor="w", padx=12, pady=(0, 6))
        frame._kpi_label = self._kpi_label
        return frame

    def _crear_tab_view(self):
        """Área de pestañas para organizar el contenido"""
        # Frame contenedor del tab view
        tab_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        tab_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Crear el tab view
        self.tab_view = ctk.CTkTabview(tab_container, fg_color=COLORS["sidebar_bg"],
                                        segmented_button_fg_color=COLORS["card_bg"],
                                        segmented_button_selected_color=COLORS["primary"],
                                        segmented_button_selected_hover_color=COLORS["primary_dark"],
                                        text_color="white", corner_radius=12)

        self.tab_view.pack(fill="both", expand=True)

        # Pestañas
        self.tab_consola = self.tab_view.add("📟 Consola")
        self.tab_resultados = self.tab_view.add("📋 Resultados")
        self.tab_graficos = self.tab_view.add("📊 Gráficos")

        # Configurar pestaña de Consola
        console_frame = ctk.CTkFrame(self.tab_consola, fg_color="transparent")
        console_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label de la consola
        ctk.CTkLabel(console_frame, text="CONSOLA DE SALIDA",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        self.text_area = ctk.CTkTextbox(console_frame, font=ctk.CTkFont(family="Consolas", size=13),
                                         wrap="word", corner_radius=10,
                                         fg_color="#0D0D1A", border_color="#333355", border_width=1)
        self.text_area.pack(fill="both", expand=True, pady=(10, 0))

        # Botones de acción para la consola
        action_frame = ctk.CTkFrame(console_frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(10, 0))

        btn_limpiar = ctk.CTkButton(action_frame, text="🗑️ Limpiar Consola", command=self.limpiar,
                                     fg_color="#333355", hover_color="#444466", height=30,
                                     font=ctk.CTkFont(size=12))
        btn_limpiar.pack(side="left", padx=(0, 10))

        btn_exportar = ctk.CTkButton(action_frame, text="📥 Exportar Reporte", command=self.exportar_reporte,
                                      fg_color=COLORS["teal"], hover_color=COLORS["teal_dark"], height=30,
                                      font=ctk.CTkFont(size=12))
        btn_exportar.pack(side="left")

        # Configurar pestaña de Resultados
        resultados_frame = ctk.CTkFrame(self.tab_resultados, fg_color="transparent")
        resultados_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(resultados_frame, text="RESULTADOS DEL ANÁLISIS",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        self.text_resultados = ctk.CTkTextbox(resultados_frame, font=ctk.CTkFont(family="Consolas", size=13),
                                               wrap="word", corner_radius=10,
                                               fg_color="#0D0D1A", border_color="#333355", border_width=1)
        self.text_resultados.pack(fill="both", expand=True, pady=(10, 0))

        # Configurar pestaña de Gráficos
        self.graficos_frame = ctk.CTkFrame(self.tab_graficos, fg_color="transparent")
        self.graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.graficos_frame, text="VISUALIZACIONES",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.graficos_placeholder = ctk.CTkLabel(self.graficos_frame, text="Los gráficos aparecerán aquí\nal ejecutar el Dashboard",
                                                  font=ctk.CTkFont(size=14), text_color="#666666")
        self.graficos_placeholder.pack(expand=True)

    def _crear_status_bar(self):
        """Barra de estado inferior"""
        status_bar = ctk.CTkFrame(self.main_content, fg_color=COLORS["sidebar_bg"], height=30, corner_radius=0)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        self.label_estado = ctk.CTkLabel(status_bar, text="💡 Sistema inactivo. Use las opciones del menú lateral.",
                                          font=ctk.CTkFont(size=11), text_color="#FFB74D")
        self.label_estado.pack(side="left", padx=15)

        self.label_info = ctk.CTkLabel(status_bar, text="v4.1 | Modo: Oscuro",
                                        font=ctk.CTkFont(size=11), text_color="#666666")
        self.label_info.pack(side="right", padx=15)

    def _crear_btn_sidebar(self, texto, comando, color, hover_color):
        """Crea un botón estilizado para el sidebar"""
        btn = ctk.CTkButton(self.sidebar, text=texto, command=comando,
                             fg_color=color, hover_color=hover_color,
                             height=42, font=ctk.CTkFont(size=13, weight="bold"),
                             corner_radius=8, anchor="w")
        btn.pack(fill="x", padx=15, pady=4)
        return btn

    # ─── FUNCIONES DE ESCRITURA ───────────────────────────────
    def escribir(self, texto):
        """Escribe en la consola principal"""
        self.text_area.insert("end", texto + "\n")
        self.text_area.see("end")
        self.root.update()

    def escribir_resultados(self, texto):
        """Escribe en la pestaña de resultados"""
        self.text_resultados.insert("end", texto + "\n")
        self.text_resultados.see("end")
        self.root.update()

    def limpiar(self):
        """Limpia la consola principal"""
        self.text_area.delete("1.0", "end")

    def limpiar_resultados(self):
        """Limpia la pestaña de resultados"""
        self.text_resultados.delete("1.0", "end")

    # ─── ACTUALIZACIÓN DE KPIs ────────────────────────────────
    def actualizar_kpis(self):
        """Actualiza los indicadores KPI del header"""
        total = len(self.estudiantes) if self.estudiantes else 0
        en_riesgo = 0
        if self.sistema and self.estudiantes:
            en_riesgo = sum(1 for e in self.estudiantes if self.sistema.predecir(e)['deserta'])

        self.kpi_total._kpi_label.configure(text=str(total))
        self.kpi_riesgo._kpi_label.configure(text=f"{en_riesgo} ({en_riesgo/max(total,1)*100:.0f}%)")

        estado_texto = "Activo" if self.sistema else "Inactivo"
        estado_color = COLORS["success"] if self.sistema else COLORS["warning"]
        self.kpi_estado._kpi_label.configure(text=estado_texto, text_color=estado_color)

    # ─── FUNCIONALIDADES PRINCIPALES ──────────────────────────
    def entrenar(self):
        """Genera datos sintéticos y entrena el sistema"""
        self.limpiar()
        self.limpiar_resultados()
        self.tab_view.set("📟 Consola")

        self.escribir("=" * 60)
        self.escribir("🔄 GENERANDO DATOS SINTÉTICOS...")
        self.escribir("=" * 60)

        self.estudiantes = self.generador.generar_dataset(n=500)
        self.escribir(f"\n✅ Generados {len(self.estudiantes)} estudiantes")

        self.sistema = SistemaPrediccionDesercion()
        self.sistema.entrenar(self.estudiantes)

        self.actualizar_kpis()
        self.label_estado.configure(text="✅ Sistema entrenado con datos SINTÉTICOS (500 estudiantes)",
                                     text_color="#81C784")
        self.escribir("\n" + "=" * 60)
        self.escribir("✅ SISTEMA LISTO PARA USAR")
        self.escribir("=" * 60)

    def cargar_excel(self):
        """Carga un archivo Excel real"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if not archivo:
            return

        self.limpiar()
        self.limpiar_resultados()
        self.tab_view.set("📟 Consola")

        self.escribir("=" * 60)
        self.escribir(f"📂 CARGANDO ARCHIVO: {os.path.basename(archivo)}")
        self.escribir("=" * 60)

        try:
            lector = LectorExcel()
            lector.cargar_datos(archivo)
            self.estudiantes = lector.convertir_a_estudiantes()

            if not self.estudiantes:
                self.escribir("\n❌ No se pudieron cargar estudiantes. Verifique el formato del archivo.")
                self.label_estado.configure(text="❌ Error al cargar Excel", text_color="#EF5350")
                return

            desertores = sum(1 for e in self.estudiantes if e.deserto)

            self.escribir(f"\n📊 ESTADÍSTICAS DEL EXCEL CARGADO:")
            self.escribir(f"   • Total estudiantes: {len(self.estudiantes)}")
            self.escribir(f"   • Desertores (histórico): {desertores} ({desertores/len(self.estudiantes)*100:.1f}%)")
            self.escribir(f"   • No desertores: {len(self.estudiantes) - desertores}")

            self.escribir("\n🔄 Entrenando el sistema con datos reales...")
            self.sistema = SistemaPrediccionDesercion()
            self.sistema.entrenar(self.estudiantes)

            self.actualizar_kpis()
            self.label_estado.configure(
                text=f"✅ Cargados {len(self.estudiantes)} estudiantes desde {os.path.basename(archivo)}",
                text_color="#81C784"
            )
            self.escribir("\n✅ SISTEMA ENTRENADO CON DATOS REALES")

        except PermissionError:
            self.escribir(f"\n❌ ERROR: No se puede acceder al archivo.")
            self.escribir(f"   El archivo '{os.path.basename(archivo)}' está siendo usado por otro programa.")
            self.escribir(f"   ")
            self.escribir(f"   💡 Solución: Cierre el archivo en Microsoft Excel (u otro programa) y vuelva a intentarlo.")
            self.label_estado.configure(text="❌ Archivo en uso. Ciérrelo en Excel e intente de nuevo.", text_color="#EF5350")
        except Exception as e:
            self.escribir(f"\n❌ Error al cargar el archivo: {str(e)}")
            self.label_estado.configure(text="❌ Error al cargar archivo", text_color="#EF5350")

    def mostrar_estadisticas(self):
        """Muestra el dashboard con estadísticas y gráficos"""
        if not self.sistema:
            self.escribir("⚠️ Primero cargue un Excel o genere datos (opciones 1 o 2)")
            return

        self.limpiar()
        self.limpiar_resultados()
        self.tab_view.set("📋 Resultados")

        total = len(self.estudiantes)
        desertores = sum(1 for e in self.estudiantes if self.sistema.predecir(e)['deserta'])
        tasa = (desertores / total) * 100 if total > 0 else 0
        notas = [e.promedio_primer_semestre for e in self.estudiantes]
        promedio_gen = sum(notas) / len(notas) if notas else 0

        # Mostrar en resultados
        self.escribir_resultados("=" * 60)
        self.escribir_resultados("📊 DASHBOARD DE ESTADÍSTICAS")
        self.escribir_resultados("=" * 60)
        self.escribir_resultados(f"\n👥 Total de estudiantes: {total}")
        self.escribir_resultados(f"⚠️ En riesgo (sistema): {desertores} ({tasa:.1f}%)")
        self.escribir_resultados(f"✅ Seguros: {total - desertores} ({(total-desertores)/total*100:.1f}%)")
        self.escribir_resultados(f"📝 Promedio global: {promedio_gen:.1f}/20")
        self.escribir_resultados(f"  Nota mínima: {min(notas):.1f}/20")
        self.escribir_resultados(f"  Nota máxima: {max(notas):.1f}/20")

        # Análisis por rango de notas
        self.escribir_resultados(f"\n📊 ESTUDIANTES EN RIESGO POR RANGO DE NOTAS:")
        rangos = [(0, 8, "0 - 8"), (8, 10, "8 - 10"), (10, 12, "10 - 12"), (12, 14, "12 - 14"), (14, 21, "14 - 20")]
        for bajo, alto, etiqueta in rangos:
            grupo = [e for e in self.estudiantes if bajo <= e.promedio_primer_semestre < alto]
            if grupo:
                riesgo = sum(1 for e in grupo if self.sistema.predecir(e)['deserta'])
                self.escribir_resultados(f"   {etiqueta}: {riesgo}/{len(grupo)} en riesgo ({riesgo/len(grupo)*100:.1f}%)")

        # ─── ABRIR DASHBOARD VISUAL ──────────────────────────
        dashboard = ctk.CTkToplevel(self.root)
        dashboard.title("📊 Dashboard - Estadísticas de Deserción")
        dashboard.geometry("1100x700")
        dashboard.attributes("-topmost", True)
        dashboard.configure(fg_color=COLORS["main_bg"])

        # Título del dashboard
        title_frame = ctk.CTkFrame(dashboard, fg_color=COLORS["sidebar_bg"], corner_radius=12)
        title_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(title_frame, text="📊 DASHBOARD DE ESTADÍSTICAS",
                      font=ctk.CTkFont(size=22, weight="bold")).pack(pady=15)

        # KPIs del dashboard
        kpi_container = ctk.CTkFrame(dashboard, fg_color="transparent")
        kpi_container.pack(fill="x", padx=20, pady=(0, 15))

        # Tarjetas KPI
        kpi_data = [
            ("👥 Total Estudiantes", str(total), COLORS["primary"]),
            ("⚠️ En Riesgo", f"{desertores} ({tasa:.1f}%)", COLORS["danger"]),
            ("✅ Seguros", f"{total - desertores} ({(total-desertores)/total*100:.1f}%)", COLORS["success"]),
            ("📝 Promedio Global", f"{promedio_gen:.1f}/20", COLORS["warning"]),
        ]

        for titulo, valor, color in kpi_data:
            card = ctk.CTkFrame(kpi_container, fg_color=COLORS["card_bg"], corner_radius=12, width=220, height=80)
            card.pack(side="left", padx=8, fill="x", expand=True)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12), text_color="#AAAAAA").pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"), text_color=color).pack(anchor="w", padx=15)

        # Gráficos
        graficos_container = ctk.CTkFrame(dashboard, fg_color=COLORS["sidebar_bg"], corner_radius=12)
        graficos_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(graficos_container, text="VISUALIZACIÓN DE DATOS",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), facecolor='#1a1a2e')

        # Gráfico de torta
        colors_pie = ['#EF5350', '#66BB6A']
        wedges, texts, autotexts = ax1.pie(
            [desertores, total - desertores],
            labels=['En Riesgo', 'Seguros'],
            colors=colors_pie,
            autopct='%1.1f%%',
            startangle=140,
            textprops={'color': 'white', 'weight': 'bold'}
        )
        ax1.set_title('Distribución de Riesgo (Predicción)', color='white', pad=15, weight='bold', fontsize=13)

        # Barras por rango de notas
        rangos_notas = [(0, 8), (8, 10), (10, 12), (12, 14), (14, 21)]
        etiquetas_rango = ['0-8', '8-10', '10-12', '12-14', '14-20']
        valores_riesgo = []
        for bajo, alto in rangos_notas:
            grupo = [e for e in self.estudiantes if bajo <= e.promedio_primer_semestre < alto]
            valores_riesgo.append(sum(1 for e in grupo if self.sistema.predecir(e)['deserta']))

        bars = ax2.bar(etiquetas_rango, valores_riesgo, color='#42A5F5', edgecolor='#1E88E5', linewidth=1.5)
        ax2.set_title('Estudiantes en Riesgo por Rango de Notas', color='white', pad=15, weight='bold', fontsize=13)
        ax2.tick_params(colors='white')
        ax2.set_ylabel('Cantidad', color='white')
        ax2.set_xlabel('Rango de Notas', color='white')
        ax2.grid(axis='y', alpha=0.2, color='white')

        for spine in ax2.spines.values():
            spine.set_edgecolor('#444466')

        for bar in bars:
            y = bar.get_height()
            if y > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2, y + 0.3, int(y),
                         ha='center', va='bottom', color='white', weight='bold', fontsize=11)

        fig.tight_layout(pad=2.0)
        canvas = FigureCanvasTkAgg(fig, master=graficos_container)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Mostrar en gráficos tab
        self.tab_view.set("📋 Resultados")
        self.escribir("\n✅ Dashboard visual abierto en ventana separada.")
        self.label_estado.configure(text="📊 Dashboard visual mostrado", text_color="#81D4FA")

    def lista_completa_riesgo(self):
        """Muestra lista completa de estudiantes en riesgo"""
        if not self.sistema:
            self.escribir("⚠️ Primero cargue un Excel o genere datos (opciones 1 o 2)")
            return

        self.limpiar()
        self.limpiar_resultados()
        self.tab_view.set("📋 Resultados")

        # Calcular lista de estudiantes en riesgo
        estudiantes_riesgo = []
        for e in self.estudiantes:
            pred = self.sistema.predecir(e)
            if pred['deserta']:
                estudiantes_riesgo.append((e, pred))

        if not estudiantes_riesgo:
            self.escribir_resultados("✅ No hay estudiantes en riesgo según el sistema.")
            return

        estudiantes_riesgo.sort(key=lambda x: x[0].promedio_primer_semestre)

        self.escribir_resultados("=" * 60)
        self.escribir_resultados(f"⚠️ LISTA COMPLETA DE ESTUDIANTES EN RIESGO ({len(estudiantes_riesgo)} total)")
        self.escribir_resultados("=" * 60)

        for i, (e, pred) in enumerate(estudiantes_riesgo, 1):
            nombre = getattr(e, 'nombre_completo', f"ID {e.id}")
            cedula = getattr(e, 'cedula', 'N/A')

            self.escribir_resultados(f"\n{i}. {nombre}")
            self.escribir_resultados(f"   ID: {e.id} | Cédula: {cedula} | "
                                      f"Nota: {e.promedio_primer_semestre}/20 | "
                                      f"Riesgo: {pred['riesgo']}")

            # Materias reprobadas
            if hasattr(e, 'notas') and e.notas:
                reprobadas = [m for m, n in e.notas.items() if n < 10]
                if reprobadas:
                    self.escribir_resultados(f"   📚 Materias reprobadas: {', '.join(reprobadas)}")

            # Factores de riesgo
            factores = []
            if e.materias_reprobadas >= 2:
                factores.append(f"{e.materias_reprobadas} materias reprobadas")
            if e.baja_asistencia:
                factores.append(f"baja asistencia ({e.asistencia_promedio}%)")
            if e.carga_alta:
                factores.append("carga alta")
            if factores:
                self.escribir_resultados(f"   ⚠️ Factores: {', '.join(factores)}")

            # Recomendación
            alerta = self.sistema.generar_alerta(e)
            if alerta and alerta.get('recomendaciones'):
                self.escribir_resultados(f"   💡 {alerta['recomendaciones'][0]}")

            self.escribir_resultados("-" * 50)

        # También mostrar resumen en consola
        self.tab_view.set("📟 Consola")
        self.escribir(f"✅ Lista generada: {len(estudiantes_riesgo)} estudiantes en riesgo.")
        self.escribir("📋 Cambie a la pestaña 'Resultados' para ver el detalle completo.")
        self.label_estado.configure(text=f"⚠️ {len(estudiantes_riesgo)} estudiantes en riesgo listados",
                                     text_color="#FFB74D")

    def diagnostico_individual(self):
        """Diagnóstico por ID de estudiante"""
        if not self.sistema:
            self.escribir("⚠️ Primero cargue un Excel o genere datos (opciones 1 o 2)")
            return

        dialog = ctk.CTkInputDialog(
            text="Ingrese el ID del estudiante:",
            title="🔍 Diagnóstico Individual"
        )
        id_text = dialog.get_input()
        if not id_text:
            return

        try:
            id_int = int(id_text)
            estudiante = next((e for e in self.estudiantes if e.id == id_int), None)

            if not estudiante:
                self.escribir(f"❌ Estudiante con ID {id_int} no encontrado")
                return

            diag = self.sistema.diagnosticar_estudiante(estudiante)
            alerta = self.sistema.generar_alerta(estudiante)
            self.mostrar_perfil_mejorado(estudiante, diag, alerta)

        except ValueError:
            self.escribir("❌ El ID debe ser un número entero")

    def buscar_y_diagnosticar(self):
        """Busca estudiantes por nombre o cédula y diagnostica"""
        if not self.sistema:
            self.escribir("⚠️ Primero cargue un Excel o genere datos (opciones 1 o 2)")
            return

        texto = self.entry_buscar.get().strip()
        if not texto:
            self.escribir("⚠️ Ingrese un nombre, apellido o cédula para buscar")
            return

        self.limpiar()
        self.limpiar_resultados()
        self.tab_view.set("📋 Resultados")

        texto_low = texto.lower()
        resultados = []

        for e in self.estudiantes:
            nombre = (getattr(e, 'nombre_completo', '') or '').lower()
            cedula = str(getattr(e, 'cedula', '')).lower()
            if texto_low in nombre or texto_low in cedula:
                resultados.append(e)

        if not resultados:
            self.escribir_resultados(f"❌ No se encontraron estudiantes con: '{texto}'")
            self.tab_view.set("📟 Consola")
            self.escribir(f"❌ No se encontraron estudiantes con: '{texto}'")
            return

        self.escribir_resultados(f"🔍 RESULTADOS DE BÚSQUEDA: '{texto}' ({len(resultados)} encontrados)")
        self.escribir_resultados("=" * 60)

        for idx, e in enumerate(resultados, 1):
            nombre = getattr(e, 'nombre_completo', f"Estudiante ID {e.id}")
            cedula = getattr(e, 'cedula', 'N/A')
            prom = e.promedio_primer_semestre
            pred = self.sistema.predecir(e)
            riesgo_txt = "⚠️ ALTO RIESGO" if pred['deserta'] else "✅ BAJO RIESGO"

            self.escribir_resultados(f"\n{idx}. {nombre}")
            self.escribir_resultados(f"   ID: {e.id} | Cédula: {cedula} | Nota: {prom}/20 | {riesgo_txt}")
            self.escribir_resultados("-" * 50)

        # Si solo hay un resultado, abrir diagnóstico automático
        if len(resultados) == 1:
            self.escribir_resultados("\n🔍 Abriendo diagnóstico automático...")
            est = resultados[0]
            diag = self.sistema.diagnosticar_estudiante(est)
            alerta = self.sistema.generar_alerta(est)
            self.mostrar_perfil_mejorado(est, diag, alerta)
        else:
            self.tab_view.set("📟 Consola")
            self.escribir(f"✅ Encontrados {len(resultados)} estudiantes.")
            self.escribir("📋 Cambie a la pestaña 'Resultados' para ver los detalles.")
            self.escribir("💡 Para diagnosticar a uno específico, anote su ID y use 'Diagnóstico Individual'")

    def mostrar_perfil_mejorado(self, estudiante, diag, alerta):
        """Muestra el perfil detallado del estudiante en ventana emergente"""
        perfil = ctk.CTkToplevel(self.root)
        titulo = getattr(estudiante, 'nombre_completo', f"ID {estudiante.id}")
        perfil.title(f"Perfil del Estudiante - {titulo}")
        perfil.geometry("1100x900")
        perfil.minsize(900, 600)
        perfil.attributes("-topmost", True)
        perfil.configure(fg_color=COLORS["main_bg"])

        # Predicción del sistema
        pred_sistema = self.sistema.predecir(estudiante)
        riesgo_real = pred_sistema['riesgo']

        # ─── CANVAS SCROLLABLE ────────────────────────────────
        canvas = ctk.CTkCanvas(perfil, bg=COLORS["main_bg"], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(perfil, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color=COLORS["main_bg"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Ajustar ancho del frame interno al canvas
        def _configure_canvas(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", _configure_canvas)

        # Scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ─── HEADER ───────────────────────────────────────────
        header = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["sidebar_bg"], corner_radius=15)
        header.pack(fill="x", padx=20, pady=15)

        # Avatar y nombre
        avatar_frame = ctk.CTkFrame(header, fg_color="transparent")
        avatar_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(avatar_frame, text="👤", font=ctk.CTkFont(size=48)).pack(side="left", padx=(0, 15))

        info_col = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(info_col, text=titulo, font=ctk.CTkFont(size=24, weight="bold"),
                      anchor="w").pack(anchor="w")

        # Información adicional
        info_parts = []
        if hasattr(estudiante, 'cedula') and estudiante.cedula:
            info_parts.append(f"Cédula: {estudiante.cedula}")
        if hasattr(estudiante, 'carrera') and estudiante.carrera:
            info_parts.append(f"Carrera: {estudiante.carrera}")
        if hasattr(estudiante, 'turno') and estudiante.turno:
            info_parts.append(f"Turno: {estudiante.turno}")

        if info_parts:
            ctk.CTkLabel(info_col, text=" | ".join(info_parts),
                          font=ctk.CTkFont(size=13), text_color="#AAAAAA",
                          anchor="w").pack(anchor="w", pady=(2, 0))

        # Etiqueta de riesgo
        color_riesgo = COLORS["danger"] if riesgo_real == "ALTO" else COLORS["success"]
        texto_riesgo = f"⚠️ {riesgo_real} RIESGO" if riesgo_real == "ALTO" else f"✅ {riesgo_real} RIESGO"

        riesgo_label = ctk.CTkLabel(avatar_frame, text=texto_riesgo,
                                     text_color=color_riesgo,
                                     font=ctk.CTkFont(size=20, weight="bold"))
        riesgo_label.pack(side="right", padx=(15, 0))

        # ─── NOTAS POR MATERIA ───────────────────────────────
        frame_notas = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["sidebar_bg"], corner_radius=15)
        frame_notas.pack(fill="x", padx=20, pady=(0, 10))

        header_notas = ctk.CTkFrame(frame_notas, fg_color="transparent")
        header_notas.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(header_notas, text="📚 NOTAS POR MATERIA",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")

        # Layout de 2 columnas para notas
        notas_container = ctk.CTkFrame(frame_notas, fg_color="transparent")
        notas_container.pack(fill="x", padx=10, pady=(0, 10))

        if hasattr(estudiante, 'notas') and estudiante.notas:
            col1 = ctk.CTkFrame(notas_container, fg_color="transparent")
            col1.pack(side="left", fill="both", expand=True, padx=5)
            col2 = ctk.CTkFrame(notas_container, fg_color="transparent")
            col2.pack(side="left", fill="both", expand=True, padx=5)

            for i, (mat, nota) in enumerate(estudiante.notas.items()):
                parent = col1 if i % 2 == 0 else col2
                color_nota = COLORS["danger"] if nota < 10 else (COLORS["warning"] if nota < 14 else COLORS["success"])

                frame_m = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], corner_radius=8)
                frame_m.pack(fill="x", pady=3)

                bg_color = "#3d1a1a" if nota < 10 else ("#3d2e1a" if nota < 14 else "#1a3d1a")
                frame_m.configure(fg_color=bg_color)

                ctk.CTkLabel(frame_m, text=f"{mat}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10, pady=6)
                ctk.CTkLabel(frame_m, text=f"{nota} / 20", text_color=color_nota,
                              font=ctk.CTkFont(weight="bold", size=13)).pack(side="right", padx=10, pady=6)
        else:
            ctk.CTkLabel(notas_container, text="No hay notas disponibles",
                          text_color="#888888").pack(pady=10)

        # Promedio
        promedio = diag['nota_real']
        color_prom = COLORS["danger"] if promedio < 10 else (COLORS["warning"] if promedio < 14 else COLORS["success"])
        frame_prom = ctk.CTkFrame(frame_notas, fg_color=COLORS["card_bg"], corner_radius=8)
        frame_prom.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(frame_prom, text=f"⭐ PROMEDIO FINAL: {promedio} / 20",
                      text_color=color_prom,
                      font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

        # ─── FACTORES DE RIESGO ──────────────────────────────
        frame_factores = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["sidebar_bg"], corner_radius=15)
        frame_factores.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(frame_factores, text="⚠️ FACTORES DE RIESGO DETECTADOS",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        if diag.get('factores'):
            for factor in diag['factores']:
                frame_f = ctk.CTkFrame(frame_factores, fg_color=COLORS["card_bg"], corner_radius=6)
                frame_f.pack(fill="x", padx=20, pady=2)
                ctk.CTkLabel(frame_f, text=f"⚠️  {factor}", text_color="#FFB74D",
                              wraplength=800, justify="left", anchor="w").pack(anchor="w", padx=10, pady=4)
        else:
            frame_f = ctk.CTkFrame(frame_factores, fg_color=COLORS["card_bg"], corner_radius=6)
            frame_f.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(frame_f, text="✅  No se detectaron factores de riesgo",
                          text_color="#A5D6A7").pack(anchor="w", padx=10, pady=4)

        # ─── RECOMENDACIONES ─────────────────────────────────
        frame_rec = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["sidebar_bg"], corner_radius=15)
        frame_rec.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(frame_rec, text="💡 RECOMENDACIONES PARA MEJORAR",
                      font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        if alerta and alerta.get('recomendaciones'):
            for rec in alerta['recomendaciones']:
                frame_r = ctk.CTkFrame(frame_rec, fg_color=COLORS["card_bg"], corner_radius=6)
                frame_r.pack(fill="x", padx=20, pady=2)
                ctk.CTkLabel(frame_r, text=f"💡  {rec}", text_color="#FFF59D",
                              wraplength=850, justify="left", anchor="w").pack(anchor="w", padx=10, pady=4)
        else:
            frame_r = ctk.CTkFrame(frame_rec, fg_color=COLORS["card_bg"], corner_radius=6)
            frame_r.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(frame_r, text="✅  Mantener el rendimiento actual. No se requieren intervenciones urgentes.",
                          text_color="#A5D6A7").pack(anchor="w", padx=10, pady=4)

        # ─── GRÁFICO DE NOTAS ────────────────────────────────
        # Calcular altura dinámica del gráfico según cantidad de materias
        num_materias = len(estudiante.notas) if hasattr(estudiante, 'notas') and estudiante.notas else 1
        altura_graf = max(3, num_materias * 0.6)  # 0.6 pulgadas por materia, mínimo 3

        frame_graf = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["sidebar_bg"], corner_radius=15)
        frame_graf.pack(fill="x", padx=20, pady=(0, 10))
        frame_graf.pack_propagate(False)
        frame_graf.configure(height=altura_graf * 100 + 80)  # Convertir a píxeles + padding

        ctk.CTkLabel(frame_graf, text="📈 ANÁLISIS VISUAL",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(10, 5))

        fig, ax = plt.subplots(figsize=(8, altura_graf), facecolor='#1a1a2e')

        if hasattr(estudiante, 'notas') and estudiante.notas:
            materias = list(estudiante.notas.keys())
            notas = list(estudiante.notas.values())
            colores = [
                COLORS["danger"] if n < 10 else (COLORS["warning"] if n < 14 else COLORS["success"])
                for n in notas
            ]
            bars = ax.barh(materias, notas, color=colores, edgecolor='white', linewidth=0.8, height=0.6)
            ax.axvline(x=10, color='white', linestyle='--', alpha=0.5, linewidth=1.5)

            # Margen derecho para las etiquetas
            max_nota = max(notas) if notas else 20
            ax.set_xlim(0, max(max_nota + 3, 20))

            ax.set_title("Notas por Materia", color='white', fontsize=13, weight='bold')
            ax.tick_params(colors='white', labelsize=10)
            ax.set_xlabel("Nota (0-20)", color='white')

            # Añadir etiquetas a las barras
            for bar, nota in zip(bars, notas):
                ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                        f"{nota:.1f}", ha='left', va='center', color='white',
                        fontsize=10, weight='bold')

            for spine in ax.spines.values():
                spine.set_edgecolor('#444466')
            ax.grid(axis='x', alpha=0.15, color='white')
            ax.set_axisbelow(True)
        else:
            ax.text(0.5, 0.5, "Sin datos de materias",
                    ha='center', va='center', color='white',
                    transform=ax.transAxes, fontsize=14)

        fig.tight_layout()
        canvas_plot = FigureCanvasTkAgg(fig, master=frame_graf)
        canvas_plot.draw()
        canvas_plot.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # ─── MENSAJE FINAL ───────────────────────────────────
        frame_msg = ctk.CTkFrame(scrollable_frame, fg_color=COLORS["card_bg"], corner_radius=10)
        frame_msg.pack(fill="x", padx=20, pady=(0, 15))

        if riesgo_real == "ALTO":
            ctk.CTkLabel(
                frame_msg,
                text="⚠️ El estudiante requiere intervención temprana. Siga las recomendaciones proporcionadas.",
                text_color=COLORS["danger"],
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(pady=10)
        else:
            ctk.CTkLabel(
                frame_msg,
                text="✅ El estudiante está en buen camino. Continúe con el seguimiento normal.",
                text_color=COLORS["success"],
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(pady=10)

    def exportar_reporte(self):
        """Exporta el contenido de la consola a un archivo de texto"""
        if not self.text_area.get("1.0", "end-1c").strip():
            messagebox.showwarning("Exportar", "No hay contenido para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            title="Guardar reporte como",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt")]
        )
        if not archivo:
            return

        try:
            with open(archivo, "w", encoding="utf-8") as f:
                contenido = self.text_area.get("1.0", "end-1c")
                if self.text_resultados.get("1.0", "end-1c").strip():
                    contenido += "\n\n" + "=" * 60 + "\n"
                    contenido += "RESULTADOS DETALLADOS\n"
                    contenido += "=" * 60 + "\n"
                    contenido += self.text_resultados.get("1.0", "end-1c")
                f.write(contenido)
            self.escribir(f"✅ Reporte exportado: {archivo}")
            messagebox.showinfo("Exportar", f"Reporte guardado exitosamente en:\n{archivo}")
        except Exception as e:
            self.escribir(f"❌ Error al exportar: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = AppMejorada()
    app.run()