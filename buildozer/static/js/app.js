/* ═══════════════════════════════════════════════════════════
   SISTEMA DE PREDICCIÓN DE DESERCIÓN - APP ANDROID
   ═══════════════════════════════════════════════════════════ */

// ─── CONFIGURACIÓN ──────────────────────────────────────────
const API_URL = 'http://localhost:5000';

// ─── INICIALIZACIÓN ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Verificar estado del servidor
    verificarServidor();
    
    // Configurar formulario
    document.getElementById('predictionForm').addEventListener('submit', enviarPrediccion);
});

// ─── FUNCIONES ──────────────────────────────────────────────

async function verificarServidor() {
    const statusText = document.getElementById('statusText');
    
    try {
        const response = await fetch(`${API_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            statusText.innerHTML = `
                <span style="color: #43A047;">✓ Servidor activo</span><br>
                Modelo ML: ${data.modelo_cargado ? '✓ Cargado' : '⚠ Modo básico'}
            `;
        } else {
            throw new Error('Servidor no responde');
        }
    } catch (error) {
        statusText.innerHTML = `
            <span style="color: #E53935;">✗ Servidor no disponible</span><br>
            <small>${error.message}</small>
        `;
    }
}

async function enviarPrediccion(event) {
    event.preventDefault();
    
    const btn = document.querySelector('.btn-primary');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Procesando...';
    btn.disabled = true;
    
    // Recopilar datos del formulario
    const datos = {
        promedio: parseFloat(document.getElementById('promedio').value),
        asistencia: parseFloat(document.getElementById('asistencia').value),
        materias_reprobadas: parseInt(document.getElementById('materias_reprobadas').value),
        carga_alta: parseInt(document.getElementById('carga_alta').value),
        trabaja: parseInt(document.getElementById('trabaja').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(datos)
        });
        
        if (!response.ok) {
            throw new Error('Error en la predicción');
        }
        
        const resultado = await response.json();
        mostrarResultado(resultado);
        
    } catch (error) {
        mostrarError(error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function mostrarResultado(resultado) {
    const resultadoDiv = document.getElementById('resultado');
    const contenidoDiv = document.getElementById('resultadoContent');
    
    resultadoDiv.style.display = 'block';
    
    const riesgoClase = resultado.riesgo > 70 ? 'riesgo-alto' : 
                        resultado.riesgo > 40 ? 'riesgo-medio' : 'riesgo-bajo';
    
    const icono = resultado.deserta ? '⚠️' : '✅';
    const mensaje = resultado.deserta ? 
        'El estudiante tiene ALTO riesgo de deserción' : 
        'El estudiante tiene BAJO riesgo de deserción';
    
    contenidoDiv.innerHTML = `
        <div class="resultado ${riesgoClase}">
            <div class="resultado-icono">${icono}</div>
            <div class="resultado-info">
                <h3>${mensaje}</h3>
                <p><strong>Nivel de Riesgo:</strong> ${resultado.riesgo}%</p>
                <p><strong>¿Deserta?:</strong> ${resultado.deserta ? 'Sí' : 'No'}</p>
                ${resultado.mensaje ? `<p><small>${resultado.mensaje}</small></p>` : ''}
            </div>
        </div>
    `;
    
    // Scroll al resultado
    resultadoDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function mostrarError(mensaje) {
    const resultadoDiv = document.getElementById('resultado');
    const contenidoDiv = document.getElementById('resultadoContent');
    
    resultadoDiv.style.display = 'block';
    contenidoDiv.innerHTML = `
        <div class="resultado error">
            <div class="resultado-icono">❌</div>
            <div class="resultado-info">
                <h3>Error en la predicción</h3>
                <p>${mensaje}</p>
            </div>
        </div>
    `;
}