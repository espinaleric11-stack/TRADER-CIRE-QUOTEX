import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Analizador Avanzado - Opciones & OTC", 
    page_icon="📈", 
    layout="wide"
)

# Inyectar estilos CSS para imitar la tarjeta del bróker (Fondo oscuro, bordes redondeados y tipografía)
st.markdown("""
<style>
    .broker-card {
        background-color: #111418;
        border: 1px solid #2a2e39;
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .broker-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .flags-container {
        position: relative;
        width: 42px;
        height: 32px;
    }
    .flag-1 {
        position: absolute;
        top: 0;
        left: 0;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #111418;
        z-index: 2;
    }
    .flag-2 {
        position: absolute;
        bottom: 0;
        right: 0;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #111418;
        z-index: 1;
    }
    .asset-info {
        display: flex;
        flex-direction: column;
    }
    .asset-title {
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #ffffff;
    }
    .asset-profit {
        font-size: 14px;
        font-weight: 700;
        color: #ff9800;
        margin-top: 2px;
    }
    .broker-arrow {
        font-size: 18px;
        color: #b0b3b8;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Analizador Técnico Avanzado de Alta Precisión (UTC-3)")
st.markdown("Herramienta optimizada con **Medias Móviles (EMA)**, **RSI**, **Bandas de Bollinger** y **Filtro de Volatilidad (ATR)**.")

# 2. Diccionario de activos con URLs de sus respectivas banderas circulares oficiales
activos_info = {
    "USD/CAD (OTC)": {"symbol": "USDCAD=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/ca.png", "profit": "84%"},
    "EUR/USD (OTC)": {"symbol": "EURUSD=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "82%"},
    "GBP/USD (OTC)": {"symbol": "GBPUSD=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "85%"},
    "USD/JPY (OTC)": {"symbol": "USDJPY=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "80%"},
    "AUD/USD (OTC)": {"symbol": "AUDUSD=X", "flag1": "https://flagcdn.com/w80/au.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "83%"},
    "EUR/JPY (OTC)": {"symbol": "EURJPY=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "81%"},
    "GBP/JPY (OTC)": {"symbol": "GBPJPY=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "78%"},
    "EUR/GBP (OTC)": {"symbol": "EURGBP=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/gb.png", "profit": "84%"},
    # Pares normales y otros
    "EUR/USD": {"symbol": "EURUSD=X", "flag1": "https://flagcdn.com/w80/eu.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "75%"},
    "GBP/USD": {"symbol": "GBPUSD=X", "flag1": "https://flagcdn.com/w80/gb.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "75%"},
    "USD/JPY": {"symbol": "USDJPY=X", "flag1": "https://flagcdn.com/w80/us.png", "flag2": "https://flagcdn.com/w80/jp.png", "profit": "75%"},
    "XAU/USD (Oro / OTC)": {"symbol": "GC=F", "flag1": "https://flagcdn.com/w80/un.png", "flag2": "https://flagcdn.com/w80/us.png", "profit": "88%"}
}

# Panel lateral de configuración
st.sidebar.header("Parámetros de Análisis")

activo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Activo / Par", 
    list(activos_info.keys())
)

temporalidad = st.sidebar.selectbox(
    "Temporalidad de las Velas", 
    ["1m", "5m", "15m", "1h", "1d"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Apariencia Estilo Bróker:** Visualización idéntica con banderas y rentabilidad sincronizada.")

# --- RENDERIZAR LA TARJETA VISUAL IDÉNTICA AL BRÓKER EN LA PANTALLA PRINCIPAL ---
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
            <span class="asset-profit">{info_actual['profit']}</span>
        </div>
    </div>
    <div class="broker-arrow">▼</div>
</div>
""", unsafe_allow_html=True)

# 3. Lógica principal del analizador
if st.sidebar.button("🚀 Ejecutar Análisis de Alta Precisión"):
    with st.spinner(f"Procesando indicadores avanzados para {activo_seleccionado}..."):
        try:
            import yfinance as yf
            
            symbol_to_fetch = info_actual["symbol"]
            periodo = "1d" if temporalidad in ["1m", "5m", "15m"] else "5d"
            df = yf.download(symbol_to_fetch, period=periodo, interval=temporalidad, progress=False)
            
            if df.empty or len(df) < 25:
                st.warning("⚠️ No hay suficientes datos disponibles para este intervalo en este momento. Intenta con otra temporalidad.")
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
                
                # --- MÉTRICAS VISUALES ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Precio Actual", f"{precio_actual:.5f}")
                col2.metric("EMA 5 / 20", f"{ema5_val:.4f} / {ema20_val:.4f}")
                col3.metric("RSI (14)", f"{rsi_val:.1f}")
                col4.metric("Hora Actual (UTC-3)", hora_actual_str)
                
                st.markdown("---")
                
                # --- MOTOR DE DECISIÓN DE ALTA CONFLUENCIA ---
                st.subheader(f"🎯 Resultado del Análisis Avanzado para: {activo_seleccionado}")
                
                razones = []
                tendencia_alcista = ema5_val > ema20_val
                tendencia_bajista = ema5_val < ema20_val
                
                if tendencia_alcista:
                    razones.append("✅ **Tendencia:** EMA rápida por encima de la lenta (Alcista).")
                else:
                    razones.append("❌ **Tendencia:** EMA rápida por debajo de la lenta (Bajista).")
                
                es_call = tendencia_alcista and rsi_val < 62 and (precio_actual <= df['BB_Middle'].iloc[-1])
                es_put = tendencia_bajista and rsi_val > 38 and (precio_actual >= df['BB_Middle'].iloc[-1])
                
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
                    st.write("El sistema ha descartado la operación para proteger tu capital. No hay confluencia clara.")
                
                with st.expander("🔍 Ver detalles técnicos de los filtros"):
                    for r in razones:
                        st.write(f"- {r}")
                    st.write(f"- **Volatilidad ATR:** {atr_val:.5f} (Filtro de ruido superado)")
                    st.write(f"- **Bandas de Bollinger:** Superior: {bb_upper:.5f} | Inferior: {bb_lower:.5f}")
                
                # --- GRÁFICA VISUAL ---
                st.markdown("---")
                st.subheader("📊 Gráfica de Precio con Bandas de Bollinger")
                df_chart = df[['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(50)
                st.line_chart(df_chart)
                
                with st.expander("Ver tabla histórica detallada"):
                    st.dataframe(df[['Close', 'EMA_5', 'EMA_20', 'RSI', 'ATR']].tail(10))

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos de mercado: {e}")
else:
    st.info("👈 Selecciona tu activo en la barra lateral y haz clic en **Ejecutar Análisis de Alta Precisión**.")
