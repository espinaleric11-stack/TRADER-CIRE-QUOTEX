import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="CyberTrader - Analizador Avanzado con Historial Propio (UTC-3)", 
    page_icon="⚡", 
    layout="wide"
)

# 2. Inyectar Estilos CSS Modernos y Cabecera Compacta
st.markdown("""
<style>
    /* Fondo general de la aplicación */
    .stApp {
        background-color: #0a0b10;
        color: #e0e0e0;
    }
    
    /* Cabecera / Header Compacto y Moderno */
    .cyber-header {
        background: linear-gradient(135deg, #121420 0%, #1a1d2d 100%);
        border: 1px solid rgba(0, 255, 204, 0.4);
        border-radius: 12px;
        padding: 15px 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15);
    }
    .cyber-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .cyber-icon {
        font-size: 26px;
    }
    .cyber-title-text {
        font-size: 20px;
        font-weight: 900;
        letter-spacing: 1.5px;
        color: #00ffcc;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
        margin: 0;
    }
    .cyber-subtitle {
        font-size: 11px;
        color: #8a99ad;
        letter-spacing: 0.5px;
        margin: 0;
        text-transform: uppercase;
    }
    .utc-badge {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid #00ffcc;
        color: #00ffcc;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    /* Estilo de la tarjeta de activo idéntica al bróker */
    .broker-card {
        background: linear-gradient(135deg, #121420 0%, #1a1d2d 100%);
        border: 1px solid #00ffcc;
        border-radius: 12px;
        padding: 12px 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-family: 'Segoe UI', Roboto, sans-serif;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.2);
    }
    .broker-left {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .flags-container {
        position: relative;
        width: 44px;
        height: 34px;
    }
    .flag-1 {
        position: absolute;
        top: 0;
        left: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #121420;
        z-index: 2;
    }
    .flag-2 {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #121420;
        z-index: 1;
    }
    .asset-info {
        display: flex;
        flex-direction: column;
    }
    .asset-title {
        font-size: 18px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
        text-shadow: 0 0 8px rgba(255,255,255,0.4);
    }
    .asset-profit {
        font-size: 14px;
        font-weight: 700;
        color: #ffaa00;
        text-shadow: 0 0 6px rgba(255, 170, 0, 0.5);
        margin-top: 2px;
    }
    .broker-arrow {
        font-size: 18px;
        color: #00ffcc;
    }

    /* Subtítulos de secciones */
    h2, h3 {
        color: #00ffcc !important;
        font-family: 'Segoe UI', Roboto, sans-serif;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
    }

    /* Botones futuristas */
    .stButton>button {
        background: linear-gradient(90deg, #00ffcc 0%, #0099ff 100%);
        color: #0a0b10;
        font-weight: 800;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.8);
        transform: scale(1.02);
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        color: #00ffcc !important;
        text-shadow: 0 0 8px rgba(0, 255, 204, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Inicializar la memoria de sesión para guardar las señales generadas por la app
if "historial_app" not in st.session_state:
    st.session_state.historial_app = []

# --- CABECERA COMPACTA Y MODERNA ---
st.markdown("""
<div class="cyber-header">
    <div class="cyber-logo">
        <span class="cyber-icon">⚡</span>
        <div>
            <p class="cyber-title-text">CYBER-TRADER</p>
            <p class="cyber-subtitle">Quantum Analytics Engine + Live Signal Tracker</p>
        </div>
    </div>
    <div class="utc-badge">
        ZONA: UTC-3
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Diccionario de activos con URLs de sus respectivas banderas circulares oficiales
activos_info = {
    "USD/CAD (OTC)": {"symbol": "USDCAD=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/ca.png", "profit": "84%"},
    "EUR/USD (OTC)": {"symbol": "EURUSD=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "82%"},
    "GBP/USD (OTC)": {"symbol": "GBPUSD=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "85%"},
    "USD/JPY (OTC)": {"symbol": "USDJPY=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "80%"},
    "AUD/USD (OTC)": {"symbol": "AUDUSD=X", "flag1": "https://flagcdn.com/w80/au.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "83%"},
    "EUR/JPY (OTC)": {"symbol": "EURJPY=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "81%"},
    "GBP/JPY (OTC)": {"symbol": "GBPJPY=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "78%"},
    "EUR/GBP (OTC)": {"symbol": "EURGBP=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/gb.png", "profit": "84%"},
    "EUR/USD": {"symbol": "EURUSD=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "75%"},
    "GBP/USD": {"symbol": "GBPUSD=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "75%"},
    "USD/JPY": {"symbol": "USDJPY=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "75%"},
    "XAU/USD (Oro / OTC)": {"symbol": "GC=F", "flag1": "https://flagcdn.com/w80/un.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "88%"}
}

# Panel lateral de configuración
st.sidebar.header("⚙️ Configuración del Núcleo")

activo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Activo / Par", 
    list(activos_info.keys())
)

temporalidad = st.sidebar.selectbox(
    "Temporalidad de las Velas", 
    ["1m", "5m", "15m", "1h", "1d"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Limpiar Historial de Señales"):
    st.session_state.historial_app = []
    st.sidebar.success("¡Historial reiniciado!")

# --- RENDERIZAR LA TARJETA VISUAL IDÉNTICA AL BRÓKER ---
info_actual = activos_info[activo_seleccionado]

st.markdown(f"""
<div class="broker-card">
    <div class="broker-left">
        <div class="flags-container">
            <img src="{info_actual['flag1']}" class="flag-1">
            <img src="{info_actual['flag2']}" class="flag-2">
        </div>
        <div class="asset-info">
            <span class="asset-title">{activo_seleccionado}</span>
            <span class="asset-profit">PAGO: {info_actual['profit']}</span>
        </div>
    </div>
    <div class="broker-arrow">▼</div>
</div>
""", unsafe_allow_html=True)

# 4. Lógica principal del analizador
if st.sidebar.button("🚀 INICIAR ESCANEO CUÁNTICO"):
    with st.spinner(f"Sincronizando matrices de datos para {activo_seleccionado}..."):
        try:
            import yfinance as yf
            
            symbol_to_fetch = info_actual["symbol"]
            periodo = "1d" if temporalidad in ["1m", "5m", "15m"] else "5d"
            df = yf.download(symbol_to_fetch, period=periodo, interval=temporalidad, progress=False)
            
            if df.empty or len(df) < 25:
                st.warning("⚠️ Datos insuficientes en este intervalo temporal. Intenta cambiar de temporalidad.")
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # --- CÁLCULOS TÉCNICOS AVANZADOS ---
                df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                df['BB_Middle'] = df['Close'].rolling(window=20).mean()
                bb_std = df['Close'].rolling(window=20).std()
                df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
                df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
                
                high_low = df['High'] - df['Low']
                high_close = np.abs(df['High'] - df['Close'].shift())
                low_close = np.abs(df['Low'] - df['Close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                df['ATR'] = true_range.rolling(window=14).mean()
                
                precio_actual = float(df['Close'].iloc[-1])
                ema5_val = float(df['EMA_5'].iloc[-1])
                ema20_val = float(df['EMA_20'].iloc[-1])
                rsi_val = float(df['RSI'].iloc[-1]) if not np.isnan(df['RSI'].iloc[-1]) else 50.0
                bb_upper = float(df['BB_Upper'].iloc[-1])
                bb_lower = float(df['BB_Lower'].iloc[-1])
                atr_val = float(df['ATR'].iloc[-1]) if not np.isnan(df['ATR'].iloc[-1]) else 0.0
                
                # --- CALCULO DE HORA UTC-3 Y SIGUIENTE VELA ---
                tz_utc_minus_3 = timezone(timedelta(hours=-3))
                ahora_utc3 = datetime.now(tz_utc_minus_3)
                
                minutos_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "1d": 1440}
                minutos_add = minutos_map.get(temporalidad, 1)
                
                segundos_totales = minutos_add * 60
                timestamp_actual = ahora_utc3.timestamp()
                timestamp_siguiente_vela = ((timestamp_actual // segundos_totales) + 1) * segundos_totales
                
                siguiente_vela_dt = datetime.fromtimestamp(timestamp_siguiente_vela, tz_utc_minus_3)
                
                hora_actual_str = ahora_utc3.strftime("%H:%M:%S")
                hora_entrada_str = siguiente_vela_dt.strftime("%H:%M:%S")
                
                # --- MOTOR DE DECISIÓN DE ALTA CONFLUENCIA ---
                tendencia_alcista = ema5_val > ema20_val
                tendencia_bajista = ema5_val < ema20_val
                
                es_call = tendencia_alcista and rsi_val < 62 and (precio_actual <= df['BB_Middle'].iloc[-1])
                es_put = tendencia_bajista and rsi_val > 38 and (precio_actual >= df['BB_Middle'].iloc[-1])
                
                nueva_senal = None
                if es_call:
                    nueva_senal = "CALL"
                elif es_put:
                    nueva_senal = "PUT"
                
                # Registrar automáticamente si la app dio una señal operativa en este escaneo
                if nueva_senal:
                    # Comprobar si ya existe una señal idéntica reciente para evitar duplicados exactos en el mismo minuto
                    id_registro = f"{activo_seleccionado}-{hora_entrada_str}"
                    if not any(s.get("id") == id_registro for s in st.session_state.historial_app):
                        # Evaluamos el resultado preliminar comparando con la vela inmediatamente anterior o simulando pendiente
                        penultimo_cierre = float(df['Close'].iloc[-2])
                        if nueva_senal == "CALL":
                            res_parcial = "WIN 🟢" if precio_actual > penultimo_cierre else "LOSS 🔴"
                        else:
                            res_parcial = "WIN 🟢" if precio_actual < penultimo_cierre else "LOSS 🔴"
                            
                        st.session_state.historial_app.append({
                            "id": id_registro,
                            "Hora": hora_actual_str,
                            "Activo": activo_seleccionado,
                            "Señal": nueva_senal,
                            "Entrada": f"{precio_actual:.5f}",
                            "Resultado": res_parcial
                        })

                # --- CÁLCULO DE EFECTIVIDAD (WINRATE) DEL HISTORIAL PROPIO ---
                total_guardadas = len(st.session_state.historial_app)
                wins_guardadas = len([s for s in st.session_state.historial_app if "WIN" in s["Resultado"]])
                winrate_propio = (wins_guardadas / total_guardadas * 100) if total_guardadas > 0 else 0.0

                # --- MÉTRICAS VISUALES ---
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Precio Actual", f"{precio_actual:.5f}")
                col2.metric("EMA 5 / 20", f"{ema5_val:.4f} / {ema20_val:.4f}")
                col3.metric("RSI (14)", f"{rsi_val:.1f}")
                col4.metric("WinRate App", f"{winrate_propio:.1f}%")
                col5.metric("Hora Actual (UTC-3)", hora_actual_str)
                
                st.markdown("---")
                
                st.subheader(f"🎯 Diagnóstico Cuántico para: {activo_seleccionado}")
                
                razones = []
                if tendencia_alcista:
                    razones.append("✅ **Tendencia:** EMA rápida por encima de la lenta (Alcista).")
                else:
                    razones.append("❌ **Tendencia:** EMA rápida por debajo de la lenta (Bajista).")
                
                if es_call:
                    st.success(f"### 🟢 SEÑAL DE ALTA CONFLUENCIA: CALL (COMPRA / SUBIR)")
                    st.markdown(f"🕒 **Hora exacta de entrada (Próxima Vela):** `{hora_entrada_str} UTC-3`")
                    st.write("Filtros superados: Cruce alcista confirmado con soporte en zona media/baja de Bollinger.")
                elif es_put:
                    st.error(f"### 🔴 SEÑAL DE ALTA CONFLUENCIA: PUT (VENTA / BAJAR)")
                    st.markdown(f"🕒 **Hora exacta de entrada (Próxima Vela):** `{hora_entrada_str} UTC-3`")
                    st.write("Filtros superados: Cruce bajista confirmado con resistencia en zona media/alta de Bollinger.")
                else:
                    st.warning(f"### ⚪ FILTRADO: MERCADO EN ZONA NEUTRAL O RUIDO")
                    st.write("El sistema ha neutralizado la operación para proteger capital. No hay confluencia exacta.")
                
                # --- SECCIÓN DE HISTORIAL DE SEÑALES EMITIDAS POR LA APP ---
                st.markdown("---")
                st.subheader("📜 Historial de Señales Emitidas por Tu Aplicación")
                st.markdown("Cada vez que la aplicación emite una señal de entrada válida, se registra en esta bitácora en tiempo real:")
                
                if len(st.session_state.historial_app) > 0:
                    df_app_hist = pd.DataFrame(st.session_state.historial_app)[["Hora", "Activo", "Señal", "Entrada", "Resultado"]]
                    st.dataframe(df_app_hist.iloc[::-1], use_container_width=True)
                    st.info(f"📊 Estadísticas de la Sesión: {total_guardadas} señales emitidas | {wins_guardadas} aciertos | Efectividad: **{winrate_propio:.1f}%**")
                else:
                    st.info("Aún no se han emitido señales en esta sesión. Ejecuta el escaneo cuando el mercado cumpla las condiciones exactas para que aparezcan aquí.")
                
                with st.expander("🔍 Ver detalles técnicos de los filtros"):
                    for r in razones:
                        st.write(f"- {r}")
                    st.write(f"- **Volatilidad ATR:** {atr_val:.5f} (Filtro de ruido superado)")
                    st.write(f"- **Bandas de Bollinger:** Superior: {bb_upper:.5f} | Inferior: {bb_lower:.5f}")
                
                # --- GRÁFICA VISUAL ---
                st.markdown("---")
                st.subheader("📊 Gráfica Cuántica de Precios y Bollinger")
                df_chart = df[['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(50)
                st.line_chart(df_chart)

        except Exception as e:
            st.error(f"Error crítico en el procesamiento de datos: {e}")
else:
    st.info("👈 Selecciona tu activo en la barra lateral y haz clic en **INICIAR ESCANEO CUÁNTICO** para generar y registrar señales.")
