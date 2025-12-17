"""
Página: Dashboard de Estadísticas
Visualización de datos y análisis del sistema OCR

Elementos de Streamlit:
- ✅ st.metric: Métricas visuales con deltas
- ✅ st.bar_chart / st.line_chart: Gráficos nativos
- ✅ st.dataframe: Tablas interactivas
- ✅ st.pyplot: Gráficos matplotlib
- ✅ Session State: Datos persistentes
- ✅ st.columns: Layout responsive
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('..')
from utils.api_utils import verificar_api
from utils.sidebar_common import render_sidebar

st.title("📊 Dashboard de Estadísticas")
st.markdown("### Análisis visual del sistema OCR")

# Renderizar sidebar común
render_sidebar()

# Verificar si hay datos
if 'historial_reconocimientos' not in st.session_state or len(st.session_state.historial_reconocimientos) == 0:
    st.info("""
    ### 📭 Sin datos aún
    
    El dashboard mostrará estadísticas una vez que realices reconocimientos de texto.
    
    **Para empezar:**
    1. Ve a cualquier página de reconocimiento (📝 📷 📁)
    2. Procesa algunas imágenes
    3. Vuelve aquí para ver análisis visuales
    
    ¡Las estadísticas se actualizan automáticamente! 📈
    """)
    st.stop()

# Cargar datos del historial
# Justificación: Session state para persistencia de datos entre sesiones
historial = st.session_state.historial_reconocimientos
stats = st.session_state.estadisticas

# KPIs principales
# Justificación: Métricas visuales para mostrar indicadores clave de rendimiento
st.markdown("### 🎯 Indicadores Clave")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reconocimientos",
        stats['total_reconocimientos'],
        delta=f"+{len(historial)} hoy" if len(historial) > 0 else None,
        help="Número total de imágenes procesadas"
    )

with col2:
    st.metric(
        "Caracteres Procesados",
        stats['total_caracteres'],
        delta=f"{stats['total_caracteres']/max(stats['total_reconocimientos'],1):.1f} por imagen",
        help="Total de caracteres reconocidos"
    )

with col3:
    conf_actual = np.mean([h['confianza_promedio'] for h in historial]) if historial else 0
    st.metric(
        "Confianza Promedio",
        f"{conf_actual*100:.1f}%",
        delta=f"{(conf_actual - 0.96)*100:+.1f}% vs modelo" if conf_actual > 0 else None,
        help="Confianza promedio del modelo (96% esperado)"
    )

with col4:
    idiomas_unicos = len(stats['idiomas_detectados'])
    st.metric(
        "Idiomas Detectados",
        idiomas_unicos,
        help="Número de idiomas diferentes identificados"
    )

st.markdown("---")

# Gráficos de análisis
# Justificación: Visualización de tendencias y patrones en los datos
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📈 Confianza por Reconocimiento")
    
    # Preparar datos para el gráfico
    if historial:
        df_confianza = pd.DataFrame([
            {
                'Reconocimiento': i+1,
                'Confianza': h['confianza_promedio'] * 100
            }
            for i, h in enumerate(historial)
        ])
        
        # Justificación: Line chart para mostrar evolución temporal
        st.line_chart(df_confianza.set_index('Reconocimiento'))
        st.caption("Evolución de la confianza del modelo a lo largo del tiempo")
    else:
        st.info("Sin datos para mostrar")

with col_right:
    st.markdown("### 🌍 Distribución de Idiomas")
    
    if stats['idiomas_detectados']:
        # Justificación: Bar chart para comparar categorías
        df_idiomas = pd.DataFrame([
            {'Idioma': idioma, 'Cantidad': count}
            for idioma, count in stats['idiomas_detectados'].items()
        ])
        st.bar_chart(df_idiomas.set_index('Idioma'))
        st.caption("Frecuencia de idiomas detectados")
    else:
        st.info("Sin datos de idiomas")

# Distribución de longitud de textos
st.markdown("### 📏 Distribución de Longitud de Textos")

if historial:
    # Justificación: Matplotlib para gráficos personalizados avanzados
    longitudes = [len(h['texto']) for h in historial]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(longitudes, bins=20, edgecolor='black', alpha=0.7, color='#1f77b4')
    ax.set_xlabel('Longitud (caracteres)')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Longitud de Textos Reconocidos')
    ax.grid(True, alpha=0.3)
    
    st.pyplot(fig)
    st.caption(f"Longitud promedio: {np.mean(longitudes):.1f} caracteres | Min: {min(longitudes)} | Max: {max(longitudes)}")
else:
    st.info("Sin datos para distribución")

# Tabla detallada del historial
# Justificación: Dataframe interactivo para exploración detallada de datos
st.markdown("---")
st.markdown("### 📋 Historial Detallado")

if historial:
    df_historial = pd.DataFrame([
        {
            'ID': i+1,
            'Texto': h['texto'][:30] + '...' if len(h['texto']) > 30 else h['texto'],
            'Longitud': h.get('num_caracteres', len(h['texto'])),
            'Confianza': f"{h['confianza_promedio']*100:.1f}%",
            'Idioma': h.get('idioma', 'N/A'),
            'Timestamp': h['timestamp'].strftime('%H:%M:%S') if 'timestamp' in h else 'N/A'
        }
        for i, h in enumerate(historial)
    ])
    
    # Configurar dataframe con columnas específicas
    st.dataframe(
        df_historial,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", help="Número de reconocimiento"),
            "Texto": st.column_config.TextColumn("Texto Reconocido", help="Vista previa del texto"),
            "Longitud": st.column_config.NumberColumn("Caracteres", help="Número de caracteres"),
            "Confianza": st.column_config.TextColumn("Confianza", help="Nivel de confianza"),
            "Idioma": st.column_config.TextColumn("Idioma", help="Idioma detectado"),
            "Timestamp": st.column_config.TextColumn("Hora", help="Momento del reconocimiento")
        }
    )
else:
    st.info("Sin historial disponible")

# Análisis de caracteres más comunes
st.markdown("---")
st.markdown("### 🔤 Análisis de Caracteres")

if historial:
    col_chars, col_stats = st.columns([2, 1])
    
    with col_chars:
        # Contar frecuencia de caracteres
        todos_caracteres = ''.join([h['texto'] for h in historial])
        from collections import Counter
        contador = Counter(todos_caracteres.replace(' ', ''))  # Excluir espacios
        
        # Top 10 caracteres más comunes
        if contador:
            top_chars = dict(contador.most_common(10))
            df_chars = pd.DataFrame([
                {'Carácter': char, 'Frecuencia': freq}
                for char, freq in top_chars.items()
            ])
            
            st.bar_chart(df_chars.set_index('Carácter'))
            st.caption("Top 10 caracteres más reconocidos")
        else:
            st.info("Sin datos de caracteres")
    
    with col_stats:
        st.markdown("**Estadísticas:**")
        total_chars = len(todos_caracteres)
        chars_unicos = len(set(todos_caracteres))
        
        st.metric("Total Caracteres", total_chars)
        st.metric("Únicos", chars_unicos)
        st.metric("Espacios", todos_caracteres.count(' '))
        
        # Calcular diversidad
        diversidad = chars_unicos / total_chars if total_chars > 0 else 0
        st.metric("Diversidad", f"{diversidad*100:.1f}%")

# Controles del dashboard
st.markdown("---")
st.markdown("### ⚙️ Controles")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

with col_ctrl1:
    # Justificación: Widget para exportar datos (funcionalidad futura)
    if st.button("📥 Exportar Datos", use_container_width=True, disabled=True):
        st.info("Funcionalidad de exportación disponible próximamente")

with col_ctrl2:
    # Justificación: Limpiar datos para reiniciar análisis
    if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary"):
        if st.session_state.get('confirmar_limpieza', False):
            st.session_state.historial_reconocimientos = []
            st.session_state.estadisticas = {
                'total_reconocimientos': 0,
                'total_caracteres': 0,
                'idiomas_detectados': {}
            }
            st.session_state.confirmar_limpieza = False
            st.success("✅ Historial limpiado")
            st.rerun()
        else:
            st.session_state.confirmar_limpieza = True
            st.warning("⚠️ Haz clic de nuevo para confirmar")

with col_ctrl3:
    # Estado de la API
    if verificar_api():
        st.success("✅ API Activa")
    else:
        st.error("❌ API Inactiva")

# Información sobre el dashboard
with st.expander("ℹ️ Sobre este Dashboard"):
    st.markdown("""
    ### 📊 Dashboard de Análisis OCR
    
    **Objetivo**: Proporcionar insights visuales sobre el uso y rendimiento del sistema.
    
    **Elementos de Streamlit utilizados:**
    
    1. **`st.metric()`**: Indicadores clave con deltas
       - Justificación: Visualización rápida de KPIs importantes
    
    2. **`st.line_chart()`**: Evolución de confianza
       - Justificación: Mostrar tendencias temporales
    
    3. **`st.bar_chart()`**: Distribución de idiomas y caracteres
       - Justificación: Comparar categorías visualmente
    
    4. **`st.pyplot()`**: Histograma personalizado
       - Justificación: Gráficos avanzados con matplotlib
    
    5. **`st.dataframe()`**: Tabla interactiva del historial
       - Justificación: Exploración detallada de datos
    
    6. **Session State**: Persistencia de estadísticas
       - Justificación: Mantener datos entre interacciones
    
    **Datos recopilados:**
    - Texto reconocido (solo para estadísticas)
    - Confianza del modelo
    - Idioma detectado
    - Timestamp de procesamiento
    
    **Privacidad**: Los datos solo se almacenan en memoria durante la sesión.
    
    ¡Todas las visualizaciones se actualizan automáticamente! 📈
    """)
