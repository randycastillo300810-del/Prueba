/* ═══════════════════════════════════════════════════════════
   SISTEMA DE PREDICCIÓN DE DESERCIÓN - LÓGICA DE LA APP
   ═══════════════════════════════════════════════════════════ */

// ─── ESTADO GLOBAL ──────────────────────────────────────────
let charts = { pie: null, bar: null };
let riesgoOriginal = [];

// ─── INICIALIZACIÓN ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Sidebar
    document.getElementById('menuBtn').onclick = () => {
        document.getElementById('sidebar').classList.add('open');
        document.getElementById('overlay').classList.add('show');
    };
    document.getElementById('closeBtn').onclick = cerrarSidebar;
    document.getElementById('overlay').onclick = cerrarSidebar;

    // Cargar estado al inicio
    actualizarStatus();
    setInterval(actualizarStatus, 30000); // cada 30s
});

function cerrarSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('overlay').classList.remove('show');
}

// ─── TOAST ──────────────────────────────────────────────────
function mostrarToast(mensaje, tipo = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = mensaje;
    toast.className = `toast ${tipo}`;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3500);
}

// ─── LOADING ────────────────────────────────────────────────
function mostrarLoading(texto = 'Procesando...') {
    document.getElementById('loadingText').textContent = texto;
    document.getElementById('loading').style.display = 'flex';
}

function ocultarLoading() {
    document.getElementById('loading').style.display = 'none';
}

// ─── OCULTAR / MOSTRAR PÁGINAS ──────────────────────────────
function ocultarTodo() {
    document.querySelectorAll('.page, .welcome-screen').forEach(el => {
        el.style.display = 'none';
    });
}

function volverInicio() {
    cerrarSidebar();
    ocultarTodo();
    document.getElementById('welcomeScreen').style.display = 'block';
}

// ─── ACTUALIZAR STATUS ──────────────────────────────────────
async function actualizarStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();

        document.getElementById('kpiTotal').textContent = data.total;
        document.getElementById('kpiRiesgo').textContent = data.activo ? `${data.en_riesgo} (${data.porcentaje_riesgo}%)` : '0';
        
        const estadoEl = document.getElementById('kpiEstado');
        estadoEl.textContent = data.activo ? 'Activo' : 'Inactivo';
        estadoEl.className = `kpi-value ${data.activo ? 'success' : 'warning'}`;
    } catch(e) {
        console.log('Error al obtener status:', e);
    }
}

// ─── 1. GENERAR DATOS ───────────────────────────────────────
async function generarDatos() {
    cerrarSidebar();
    mostrarLoading('Generando datos sintéticos...');
    try {
        const res = await fetch('/api/generar', { method: 'POST' });
        const data = await res.json();
        ocultarLoading();
        mostrarToast(data.mensaje, data.exito ? 'success' : 'error');
        await actualizarStatus();
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error de conexión con el servidor', 'error');
    }
}

// ─── 2. CARGAR EXCEL ────────────────────────────────────────
async function cargarExcel(input) {
    const archivo = input.files[0];
    if (!archivo) return;
    
    cerrarSidebar();
    mostrarLoading('Cargando archivo Excel...');
    
    const formData = new FormData();
    formData.append('archivo', archivo);
    
    try {
        const res = await fetch('/api/cargar_excel', { method: 'POST', body: formData });
        const data = await res.json();
        ocultarLoading();
        mostrarToast(data.mensaje, data.exito ? 'success' : 'error');
        await actualizarStatus();
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error al cargar archivo', 'error');
    }
    
    input.value = '';
}

// ─── 3. DASHBOARD ───────────────────────────────────────────
async function mostrarDashboard() {
    cerrarSidebar();
    mostrarLoading('Cargando dashboard...');
    
    try {
        const res = await fetch('/api/estadisticas');
        const data = await res.json();
        ocultarLoading();
        
        if (!data.exito) {
            mostrarToast(data.mensaje, 'error');
            return;
        }
        
        ocultarTodo();
        document.getElementById('dashboardPage').style.display = 'block';
        
        // KPIs
        document.getElementById('dashboardKpis').innerHTML = `
            <div class="dashboard-kpi">
                <span class="kpi-label">👥 Total</span>
                <span class="kpi-val" style="color:#1E88E5">${data.total}</span>
            </div>
            <div class="dashboard-kpi">
                <span class="kpi-label">⚠️ En Riesgo</span>
                <span class="kpi-val" style="color:#E53935">${data.en_riesgo} (${data.porcentaje_riesgo}%)</span>
            </div>
            <div class="dashboard-kpi">
                <span class="kpi-label">✅ Seguros</span>
                <span class="kpi-val" style="color:#43A047">${data.seguros} (${(100 - data.porcentaje_riesgo).toFixed(1)}%)</span>
            </div>
            <div class="dashboard-kpi">
                <span class="kpi-label">📝 Promedio</span>
                <span class="kpi-val" style="color:#FB8C00">${data.promedio_global}/20</span>
            </div>
        `;
        
        // Gráfico de torta
        const pieCtx = document.getElementById('pieChart').getContext('2d');
        if (charts.pie) charts.pie.destroy();
        charts.pie = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['En Riesgo', 'Seguros'],
                datasets: [{
                    data: [data.en_riesgo, data.seguros],
                    backgroundColor: ['#E53935', '#43A047'],
                    borderColor: ['#C62828', '#2E7D32'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#ffffff', padding: 12 }
                    },
                    title: {
                        display: true,
                        text: 'Distribución de Riesgo',
                        color: '#ffffff',
                        font: { size: 14, weight: 'bold' }
                    }
                }
            }
        });
        
        // Gráfico de barras
        const barCtx = document.getElementById('barChart').getContext('2d');
        if (charts.bar) charts.bar.destroy();
        
        const rangos = data.riesgo_por_rango || [];
        charts.bar = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: rangos.map(r => r.rango),
                datasets: [{
                    label: 'En Riesgo',
                    data: rangos.map(r => r.en_riesgo),
                    backgroundColor: '#42A5F5',
                    borderColor: '#1E88E5',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Riesgo por Rango de Notas',
                        color: '#ffffff',
                        font: { size: 14, weight: 'bold' }
                    }
                },
                scales: {
                    x: { ticks: { color: '#aaaaaa' }, grid: { color: '#333355' } },
                    y: { ticks: { color: '#aaaaaa' }, grid: { color: '#333355' }, beginAtZero: true }
                }
            }
        });
        
        // Tabla de rangos
        let tableHTML = '<div class="table-row"><span class="label">📊 Rango</span><span class="label">En Riesgo/Total</span><span class="label">%</span></div>';
        rangos.forEach(r => {
            tableHTML += `
                <div class="table-row">
                    <span class="label">${r.rango}</span>
                    <span class="value">${r.en_riesgo}/${r.total}</span>
                    <span class="value" style="color:${r.porcentaje > 50 ? '#E53935' : '#43A047'}">${r.porcentaje}%</span>
                </div>
            `;
        });
        document.getElementById('rangoTable').innerHTML = tableHTML;
        
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error al cargar dashboard', 'error');
    }
}

// ─── 4. LISTA EN RIESGO ─────────────────────────────────────
async function mostrarListaRiesgo() {
    cerrarSidebar();
    mostrarLoading('Cargando lista de riesgo...');
    
    try {
        const res = await fetch('/api/lista_riesgo');
        const data = await res.json();
        ocultarLoading();
        
        if (!data.exito) {
            mostrarToast(data.mensaje, 'error');
            return;
        }
        
        ocultarTodo();
        document.getElementById('riesgoPage').style.display = 'block';
        
        riesgoOriginal = data.estudiantes || [];
        mostrarRiesgoItems(riesgoOriginal);
        
        if (data.total === 0) {
            mostrarToast('✅ No hay estudiantes en riesgo', 'info');
        }
        
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error al cargar lista', 'error');
    }
}

function mostrarRiesgoItems(items) {
    const container = document.getElementById('riesgoList');
    
    if (items.length === 0) {
        container.innerHTML = '<p style="text-align:center;color:var(--text-secondary);padding:20px">✅ No hay estudiantes en riesgo con ese filtro</p>';
        return;
    }
    
    container.innerHTML = items.map(e => `
        <div class="riesgo-item" onclick="mostrarDiagnostico(${e.id})">
            <div class="nombre">⚠️ ${e.nombre}</div>
            <div class="detalle">ID: ${e.id} | Cédula: ${e.cedula || 'N/A'} | Nota: ${e.nota}/20</div>
            ${e.factores && e.factores.length ? `<div class="factores">📋 ${e.factores.join(' · ')}</div>` : ''}
            ${e.recomendacion ? `<div style="font-size:11px;color:#FFF59D;margin-top:4px">💡 ${e.recomendacion}</div>` : ''}
        </div>
    `).join('');
}

function filtrarRiesgo() {
    const texto = document.getElementById('riesgoSearch').value.toLowerCase().trim();
    if (!texto) {
        mostrarRiesgoItems(riesgoOriginal);
        return;
    }
    const filtrados = riesgoOriginal.filter(e => 
        e.nombre.toLowerCase().includes(texto) || 
        (e.cedula && e.cedula.toLowerCase().includes(texto))
    );
    mostrarRiesgoItems(filtrados);
}

// ─── 5. BÚSQUEDA ────────────────────────────────────────────
function mostrarBusqueda() {
    cerrarSidebar();
    ocultarTodo();
    document.getElementById('busquedaPage').style.display = 'block';
    document.getElementById('searchResults').innerHTML = '';
    document.getElementById('searchInput').value = '';
    document.getElementById('searchInput').focus();
}

async function buscarEstudiante() {
    const texto = document.getElementById('searchInput').value.trim();
    if (!texto) {
        mostrarToast('⚠️ Ingrese un nombre o cédula', 'error');
        return;
    }
    
    mostrarLoading('Buscando...');
    
    try {
        const res = await fetch(`/api/buscar?q=${encodeURIComponent(texto)}`);
        const data = await res.json();
        ocultarLoading();
        
        const container = document.getElementById('searchResults');
        
        if (!data.exito) {
            container.innerHTML = `<p style="text-align:center;color:var(--text-secondary);padding:20px">${data.mensaje}</p>`;
            return;
        }
        
        if (data.total === 0) {
            container.innerHTML = `<p style="text-align:center;color:var(--text-secondary);padding:20px">❌ No se encontraron estudiantes con "${texto}"</p>`;
            return;
        }
        
        if (data.total === 1) {
            // Solo un resultado, mostrar diagnóstico directo
            mostrarDiagnostico(data.estudiantes[0].id);
            return;
        }
        
        // Múltiples resultados
        container.innerHTML = `<p style="margin-bottom:12px;color:var(--text-secondary)">🔍 ${data.total} estudiante(s) encontrado(s):</p>` +
            data.estudiantes.map(e => `
                <div class="riesgo-item" onclick="mostrarDiagnostico(${e.id})" style="border-left-color:${e.deserta ? 'var(--danger)' : 'var(--success)'}">
                    <div class="nombre">${e.deserta ? '⚠️' : '✅'} ${e.nombre}</div>
                    <div class="detalle">ID: ${e.id} | Cédula: ${e.cedula} | Nota: ${e.nota_promedio}/20</div>
                    <div class="detalle">${e.info_adicional || ''}</div>
                </div>
            `).join('');
        
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error en la búsqueda', 'error');
    }
}

// ─── 6. DIAGNÓSTICO ─────────────────────────────────────────
async function mostrarDiagnostico(id) {
    mostrarLoading('Cargando diagnóstico...');
    
    try {
        const res = await fetch(`/api/diagnostico/${id}`);
        const data = await res.json();
        ocultarLoading();
        
        if (!data.exito) {
            mostrarToast(data.mensaje, 'error');
            return;
        }
        
        ocultarTodo();
        document.getElementById('diagnosticoPage').style.display = 'block';
        
        const e = data.estudiante;
        const esAlto = e.riesgo === 'ALTO';
        
        // Notas por materia
        const notasKeys = Object.keys(e.notas_materias || {});
        let notasHTML = notasKeys.map(m => {
            const n = e.notas_materias[m];
            const cls = n < 10 ? 'reprobado' : (n < 14 ? 'regular' : 'bueno');
            return `<div class="nota-item"><span>${m}</span><span class="nota-val ${cls}">${n} / 20</span></div>`;
        }).join('');
        
        if (!notasHTML) notasHTML = '<p style="color:var(--text-muted);text-align:center">Sin notas disponibles</p>';
        
        document.getElementById('diagnosticoContent').innerHTML = `
            <!-- Header -->
            <div class="diag-header">
                <div class="diag-avatar">👤</div>
                <div class="diag-info">
                    <h3>${e.nombre}</h3>
                    <p>${e.cedula} | ${e.info_adicional || ''}</p>
                </div>
                <div class="diag-riesgo ${esAlto ? 'alto' : 'bajo'}">
                    ${esAlto ? '⚠️ ALTO' : '✅ BAJO'} RIESGO
                </div>
            </div>
            
            <!-- Notas -->
            <div class="diag-section">
                <h4>📚 NOTAS POR MATERIA</h4>
                ${notasHTML}
                <div class="diag-promedio" style="color:${e.promedio_final < 10 ? 'var(--danger)' : (e.promedio_final < 14 ? 'var(--warning)' : 'var(--success)')}">
                    ⭐ PROMEDIO FINAL: ${e.promedio_final} / 20
                </div>
            </div>
            
            <!-- Detalles -->
            <div class="diag-section">
                <h4>📋 DETALLES ACADÉMICOS</h4>
                <div class="nota-item"><span>Materias Reprobadas</span><span class="nota-val ${e.materias_reprobadas >= 2 ? 'reprobado' : 'bueno'}">${e.materias_reprobadas}</span></div>
                <div class="nota-item"><span>Asistencia</span><span class="nota-val ${e.baja_asistencia ? 'reprobado' : 'bueno'}">${e.asistencia}%</span></div>
                <div class="nota-item"><span>Carga Alta</span><span class="nota-val ${e.carga_alta ? 'reprobado' : 'bueno'}">${e.carga_alta ? 'Sí' : 'No'}</span></div>
                <div class="nota-item"><span>Trabaja</span><span>${e.trabaja ? `Sí (${e.horas_trabajo}h)` : 'No'}</span></div>
            </div>
            
            <!-- Factores -->
            <div class="diag-section">
                <h4>⚠️ FACTORES DE RIESGO</h4>
                ${(e.factores && e.factores.length) ? e.factores.map(f => `<div class="factor-item">⚠️  ${f}</div>`).join('') : '<div class="factor-item" style="color:var(--success)">✅ No se detectaron factores de riesgo</div>'}
            </div>
            
            <!-- Recomendaciones -->
            <div class="diag-section">
                <h4>💡 RECOMENDACIONES</h4>
                ${(e.recomendaciones && e.recomendaciones.length) ? e.recomendaciones.map(r => `<div class="rec-item">💡  ${r}</div>`).join('') : '<div class="rec-item" style="color:var(--success)">✅ Mantener el rendimiento actual</div>'}
            </div>
            
            <!-- Footer -->
            <div class="diag-footer ${esAlto ? 'alto' : 'bajo'}">
                ${esAlto ? '⚠️ El estudiante requiere intervención temprana.' : '✅ El estudiante está en buen camino.'}
            </div>
        `;
        
    } catch(e) {
        ocultarLoading();
        mostrarToast('❌ Error al cargar diagnóstico', 'error');
    }
}

function volverBusqueda() {
    ocultarTodo();
    document.getElementById('busquedaPage').style.display = 'block';
}