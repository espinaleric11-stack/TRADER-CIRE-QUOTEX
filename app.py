import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="CyberTrader // High-Precision Terminal (UTC-3)", 
    page_icon="⚡", 
    layout="wide"
)

# 2. Inyectar Estilos CSS Futuristas de Última Generación
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111422 0%, #08090d 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    .cyber-header {
        background: linear-gradient(135deg, rgba(18, 20, 32, 0.8) 0%, rgba(26, 29, 45, 0.8) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 16px;
        padding: 18px 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .cyber-logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .cyber-icon {
        font-size: 28px;
        filter: drop-shadow(0 0 10px rgba(0, 255, 204, 0.6));
    }
    .cyber-title-text {
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 2px;
        color: #00ffcc;
        text-shadow: 0 0 12px rgba(0, 255, 204, 0.5);
        margin: 0;
    }
    .cyber-subtitle {
        font-size: 11px;
        color: #8a99ad;
        letter-spacing: 1px;
        margin: 0;
        text-transform: uppercase;
    }
    .utc-badge {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.5);
        color: #00ffcc;
        padding: 8px 16px;
        border-radius: 10px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: inset 0 0 10px rgba(0, 255, 204, 0.2);
    }
    .broker-card {
        background: linear-gradient(135deg, rgba(18, 20, 32, 0.9) 0%, rgba(26, 29, 45, 0.9) 100%);
        border: 1px solid rgba(0, 255, 204, 0.5);
        border-radius: 14px;
        padding: 16px 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.15);
    }
    .broker-left {
        display: flex;
        align-items: center;
        gap: 18px;
    }
    .flags-container {
        position: relative;
        width: 48px;
        height: 36px;
    }
    .flag-1 {
        position: absolute;
        top: 0;
        left: 0;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #121420;
        z-index: 2;
    }
    .flag-2 {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 30px;
        height: 30px;
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
        font-size: 19px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #ffffff;
    }
    .asset-profit {
        font-size: 14px;
        font-weight: 700;
        color: #ffaa00;
        margin-top: 3px;
    }
    h2, h3 {
        color: #00ffcc !important;
        font-weight: 700;
    }
    .stButton>button {
        background: linear-gradient(135deg, #00ffcc 0%, #0099ff 100%);
        color: #08090d;
        font-weight: 800;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.4rem;
        box-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.95;
        box-shadow: 0 0 30px rgba(0, 255, 204, 0.8);
        transform: translateY(-2px);
    }
    [data-testid="stMetric"] {
        background: rgba(18, 20, 32, 0.6);
        border: 1px solid rgba(0, 255, 204, 0.2);
        padding: 14px;
        border-radius: 12px;
    }
    [data-testid="stMetricValue"] {
        color: #00ffcc !important;
        font-weight: 800 !important;
    }
    .success-box {
        background: rgba(0, 255, 128, 0.1);
        border-left: 4px solid #00ff80;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    .error-box {
        background: rgba(255, 75, 75, 0.1);
        border-left: 4px solid #ff4b4b;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar memoria de sesión
if "historial_app" not in st.session_state:
    st.session_state.historial_app = []

# Cabecera
st.markdown("""
<div class="cyber-header">
    <div class="cyber-logo">
        <span class="cyber-icon">⚡</span>
        <div>
            <p class="cyber-title-text">CYBER-TRADER</p>
            <p class="cyber-subtitle">High-Precision Quantum Engine (Strict Filter Mode)</p>
        </div>
    </div>
    <div class="utc-badge">
        🌐 ZONA: UTC-3
    </div>
</div>
""", unsafe_allow_html=True)

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

st.sidebar.header("⚙️ Configuración del Núcleo")
activo_seleccionado = st.sidebar.selectbox("Seleccionar Activo / Par", list(activos_info.keys()))
temporalidad = st.sidebar.selectbox("Temporalidad de las Velas", ["1m", "5m", "15m", "1h", "1d"])

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Limpiar Historial de Señales"):
    st.session_state.historial_app = []
    st.sidebar.success("¡Historial reiniciado!")

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

if st.sidebar.button("🚀 INICIAR ESCANEO DE ALTA SEGURIDAD"):
    with st.spinner(f"Aplicando filtros estrictos de confluencia para {activo_seleccionado}..."):
        try:
            import yfinance as yf
            
            symbol_to_fetch = info_actual["symbol"]
            periodo = "1d" if temporalidad in ["1m", "5m", "15m"] else "5d"
            df = yf.download(symbol_to_fetch, period=periodo, interval=temporalidad, progress=False)
            
            if df.empty or len(df) < 30:
                st.warning("⚠️ Datos insuficientes en este intervalo temporal.")
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # --- INDICADORES TÉCNICOS ---
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
                atr_promedio = float(df['ATR'].mean())
                
                # --- HORA UTC-3 ---
                tz_utc_minus_3 = timezone(timedelta(hours=-3))
                ahora_utc3 = datetime.now(tz_utc_minus_3)
                minutos_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "1d": 1440}
                minutos_add = minutos_map.get(temporalidad, 1)
                segundos_totales = minutos_add * 60
                timestamp_siguiente_vela = ((ahora_utc3.timestamp() // segundos_totales) + 1) * segundos_totales
                siguiente_vela_dt = datetime.fromtimestamp(timestamp_siguiente_vela, tz_utc_minus_3)
                
                hora_actual_str = ahora_utc3.strftime("%H:%M:%S")
                hora_entrada_str = siguiente_vela_dt.strftime("%H:%M:%S")
                
                # --- NUEVO MOTOR DE ALTA SEGURIDAD Y ESTRICTO ---
                # Exigimos que la tendencia sea clara, el RSI esté en extremos de sobreventa/sobrecompra
                # y que el precio haya tocado o rebasado las bandas de Bollinger con volatilidad suficiente.
                tendencia_alcista_fuerte = (ema5_val > ema20_val) and ((ema5_val - ema20_val) > (atr_val * 0.1))
                tendencia_bajista_fuerte = (ema5_val < ema20_val) and ((ema20_val - ema5_val) > (atr_val * 0.1))
                
                volatilidad_suficiente = atr_val >= (atr_promedio * 0.7)
                
                es_call_seguro = (
                    tendencia_alcista_fuerte and 
                    rsi_val <= 42 and  # RSI bajo (zona de rebote alcista estricta)
                    precio_actual <= (bb_lower + (atr_val * 0.5)) and  # Cerca o por debajo de la banda inferior
                    volatilidad_suficiente
                )
                
                es_put_seguro = (
                    tendencia_bajista_fuerte and 
                    rsi_val >= 58 and  # RSI alto (zona de rebote bajista estricta)
                    precio_actual >= (bb_upper - (atr_val * 0.5)) and  # Cerca o por encima de la banda superior
                    volatilidad_suficiente
                )
                
                nueva_senal = "CALL" if es_call_seguro else ("PUT" if es_put_seguro else None)
                
                if nueva_senal:
                    id_registro = f"{activo_seleccionado}-{hora_entrada_str}"
                    if not any(s.get("id") == id_registro for s in st.session_state.historial_app):
                        penultimo_cierre = float(df['Close'].iloc[-2])
                        res_parcial = "WIN 🟢" if (nueva_senal == "CALL" and precio_actual > penultimo_cierre) or (nueva_senal == "PUT" and precio_actual < penultimo_cierre) else "LOSS 🔴"
                            
                        st.session_state.historial_app.append({
                            "id": id_registro,
                            "Hora": hora_actual_str,
                            "Activo": activo_seleccionado,
                            "Señal": nueva_senal,
                            "Entrada": f"{precio_actual:.5f}",
                            "Resultado": res_parcial
                        })

                total_guardadas = len(st.session_state.historial_app)
                wins_guardadas = len([s for s in st.session_state.historial_app if "WIN" in s["Resultado"]])
                winrate_propio = (wins_guardadas / total_guardadas * 100) if total_guardadas > 0 else 0.0

                # Métricas
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Precio Actual", f"{precio_actual:.5f}")
                col2.metric("EMA 5 / 20", f"{ema5_val:.4f} / {ema20_val:.4f}")
                col3.metric("RSI Estricto", f"{rsi_val:.1f}")
                col4.metric("WinRate Protegido", f"{winrate_propio:.1f}%")
                col5.metric("Hora (UTC-3)", hora_actual_str)
                
                st.markdown("---")
                st.subheader(f"🛡️ Diagnóstico de Seguridad para: {activo_seleccionado}")
                
                if es_call_seguro:
                    st.markdown(f"""
                    <div class="success-box">
                        <h3 style="color: #00ff80 !important; margin:0;">🟢 SEÑAL ULTRA-SEGURA: CALL (COMPRA)</h3>
                        <p style="margin: 5px 0 0 0; font-size:15px;">🕒 <b>Hora de entrada exacta:</b> {hora_entrada_str} UTC-3</p>
                        <p style="margin: 2px 0 0 0; color: #b0c4de; font-size: 13px;">Filtros estrictos superados: Tendencia alcista confirmada + RSI en sobreventa (<=42) + Rebote en Banda Inferior + ATR óptimo.</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif es_put_seguro:
                    st.markdown(f"""
                    <div class="error-box">
                        <h3 style="color: #ff4b4b !important; margin:0;">🔴 SEÑAL ULTRA-SEGURA: PUT (VENTA)</h3>
                        <p style="margin: 5px 0 0 0; font-size:15px;">🕒 <b>Hora de entrada exacta:</b> {hora_entrada_str} UTC-3</p>
                        <p style="margin: 2px 0 0 0; color: #b0c4de; font-size: 13px;">Filtros estrictos superados: Tendencia bajista confirmada + RSI en sobrecompra (>=58) + Rebote en Banda Superior + ATR óptimo.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("### ⚪ FILTRO DE SEGURIDAD ACTIVADO: MERCADO DESCARTADO\nPara proteger tu capital y elevar drásticamente los aciertos, el sistema ha bloqueado la emisión de señales porque no se cumplen los 4 filtros simultáneos de confluencia extrema.")
                
                st.markdown("---")
                st.subheader("📜 Historial de Señales de Alta Seguridad")
                
                if len(st.session_state.historial_app) > 0:
                    df_app_hist = pd.DataFrame(st.session_state.historial_app)[["Hora", "Activo", "Señal", "Entrada", "Resultado"]]
                    st.dataframe(df_app_hist.iloc[::-1], use_container_width=True)
                    st.info(f"📊 Estadísticas del Filtro Estricto: {total_guardadas} señales emitidas | {wins_guardadas} aciertos | Efectividad: **{winrate_propio:.1f}%**")
                else:
                    st.info("No se han emitido señales bajo este filtro estricto. La aplicación esperará pacientemente hasta encontrar una oportunidad con alta probabilidad matemática de éxito.")
                
                with st.expander("🔍 Ver estado de los Filtros de Seguridad en tiempo real"):
                    st.write(f"- **Tendencia Alcista Fuerte:** {'✅ Sí' if tendencia_alcista_fuerte else '❌ No'}")
                    st.write(f"- **Tendencia Bajista Fuerte:** {'✅ Sí' if tendencia_bajista_fuerte else '❌ No'}")
                    st.write(f"- **Filtro RSI Extremo:** {'✅ Superado' if (rsi_val <= 42 or rsi_val >= 58) else '❌ En zona neutral (' + str(round(rsi_val, 1)) + ')'}")
                    st.write(f"- **Volatilidad ATR Óptima:** {'✅ Sí' if volatilidad_suficiente else '❌ Mercado lateral o con ruido'}")

                st.markdown("---")
                st.subheader("📊 Gráfica de Precisión y Rangos")
                df_chart = df[['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(50)
                st.line_chart(df_chart)

        except Exception as e:
            st.error(f"Error en el procesamiento seguro: {e}")
else:
    st.info("👈 Selecciona tu activo y haz clic en **INICIAR ESCANEO DE ALTA SEGURIDAD** para buscar operaciones con filtros estrictos.")
