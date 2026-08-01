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

st.title("📈 Analizador Técnico Avanzado de Alta Precisión (UTC-3)")
st.markdown("Herramienta optimizada con **Medias Móviles (EMA)**, **RSI**, **Bandas de Bollinger** y **Filtro de Volatilidad (ATR)** para reducir señales falsas.")

# 2. Panel lateral de configuración
st.sidebar.header("Parámetros de Análisis")

activo = st.sidebar.selectbox(
    "Seleccionar Activo / Par", 
    [
        # Pares OTC
        "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/CAD (OTC)", "USD/JPY (OTC)", 
        "AUD/USD (OTC)", "EUR/JPY (OTC)", "GBP/JPY (OTC)", "EUR/GBP (OTC)",
        # Forex Principales
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "NZD/USD", "USD/CHF",
        # Metales
        "XAU/USD (Oro / OTC)", "GC=F (Oro Estándar)",
        # Criptomonedas
        "BTC/USD", "ETH/USD"
    ]
)

temporalidad = st.sidebar.selectbox(
    "Temporalidad de las Velas", 
    ["1m", "5m", "15m", "1h", "1d"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Filtro de Alta Calidad Activo:** Las señales ahora exigen confluencia entre tendencia (EMA), momento (RSI) y volatilidad (Bollinger/ATR).")

# 3. Lógica principal del analizador
if st.sidebar.button("🚀 Ejecutar Análisis de Alta Precisión"):
    with st.spinner(f"Procesando indicadores avanzados para {activo}..."):
        try:
            import yfinance as yf
            
            simbolo_map = {
                "EUR/USD (OTC)": "EURUSD=X",
                "GBP/USD (OTC)": "GBPUSD=X",
                "USD/CAD (OTC)": "USDCAD=X",
                "USD/JPY (OTC)": "USDJPY=X",
                "AUD/USD (OTC)": "AUDUSD=X",
                "EUR/JPY (OTC)": "EURJPY=X",
                "GBP/JPY (OTC)": "GBPJPY=X",
                "EUR/GBP (OTC)": "EURGBP=X",
                "EUR/USD": "EURUSD=X",
                "GBP/USD": "GBPUSD=X",
                "USD/JPY": "USDJPY=X",
                "AUD/USD": "AUDUSD=X",
                "USD/CAD": "USDCAD=X",
                "NZD/USD": "NZDUSD=X",
                "USD/CHF": "USDCHF=X",
                "XAU/USD (Oro / OTC)": "GC=F",
                "BTC/USD": "BTC-USD",
                "ETH/USD": "ETH-USD"
            }
            
            symbol_to_fetch = simbolo_map.get(activo, "EURUSD=X")
            
            periodo = "1d" if temporalidad in ["1m", "5m", "15m"] else "5d"
            df = yf.download(symbol_to_fetch, period=periodo, interval=temporalidad, progress=False)
            
            if df.empty or len(df) < 25:
                st.warning("⚠️ No hay suficientes datos disponibles para este intervalo en este momento. Intenta con otra temporalidad.")
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # --- CÁLCULOS TÉCNICOS AVANZADOS ---
                # 1. EMAs
                df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                
                # 2. RSI (14)
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                # 3. Bandas de Bollinger (20 periodos, 2 desviaciones estándar)
                df['BB_Middle'] = df['Close'].rolling(window=20).mean()
                bb_std = df['Close'].rolling(window=20).std()
                df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
                df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
                
                # 4. Filtro ATR (Average True Range para volatilidad)
                high_low = df['High'] - df['Low']
                high_close = np.abs(df['High'] - df['Close'].shift())
                low_close = np.abs(df['Low'] - df['Close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                df['ATR'] = true_range.rolling(window=14).mean()
                
                # Extraer valores actuales
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
                st.subheader(f"🎯 Resultado del Análisis Avanzado para: {activo}")
                
                razones = []
                
                # Evaluación de tendencia
                tendencia_alcista = ema5_val > ema20_val
                tendencia_bajista = ema5_val < ema20_val
                
                if tendencia_alcista:
                    razones.append("✅ **Tendencia:** EMA rápida por encima de la lenta (Alcista).")
                else:
                    razones.append("❌ **Tendencia:** EMA rápida por debajo de la lenta (Bajista).")
                
                # Evaluación de RSI y Bollinger
                filtro_rsi_call = rsi_val < 60 and rsi_val > 30
                filtro_rsi_put = rsi_val > 40 and rsi_val < 70
                
                cerca_banda_inferior = precio_actual <= (bb_lower * 1.002)
                cerca_banda_superior = precio_actual >= (bb_upper * 0.998)
                
                # Condiciones estrictas para disparar la señal de alta calidad
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
                    st.write("El sistema ha descartado la operación para proteger tu capital. No hay confluencia clara entre las Bandas de Bollinger y las EMAs.")
                
                with st.expander("🔍 Ver detalles técnicos de los filtros"):
                    for r in razones:
                        st.write(f"- {r}")
                    st.write(f"- **Volatilidad ATR:** {atr_val:.5f} (Filtro de ruido superado)")
                    st.write(f"- **Bandas de Bollinger:** Superior: {bb_upper:.5f} | Inferior: {bb_lower:.5f}")
                
                # --- GRÁFICA VISUAL DE PRECIOS Y BOLINGER ---
                st.markdown("---")
                st.subheader("📊 Gráfica de Precio con Bandas de Bollinger")
                
                df_chart = df[['Close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(50)
                st.line_chart(df_chart)
                
                with st.expander("Ver tabla histórica detallada"):
                    st.dataframe(df[['Close', 'EMA_5', 'EMA_20', 'RSI', 'ATR']].tail(10))

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos de mercado: {e}")
else:
    st.info("👈 Selecciona tu activo y temporalidad en la barra lateral y haz clic en **Ejecutar Análisis de Alta Precisión**.")
