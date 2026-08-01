import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Analizador Técnico - Opciones & OTC", 
    page_icon="📈", 
    layout="wide"
)

st.title("📈 Analizador Técnico Independiente (UTC-3)")
st.markdown("Herramienta de análisis en tiempo real con marcas de tiempo exactas para la siguiente vela (Zona horaria: **UTC-3**).")

# 2. Panel lateral de configuración
st.sidebar.header("Parámetros de Análisis")

activo = st.sidebar.selectbox(
    "Seleccionar Activo / Par", 
    [
        # Pares OTC (Formato de bróker)
        "EUR/USD (OTC)", "GBP/USD (OTC)", "USD/CAD (OTC)", "USD/JPY (OTC)", 
        "AUD/USD (OTC)", "EUR/JPY (OTC)", "GBP/JPY (OTC)", "EUR/GBP (OTC)",
        # Forex Principales (Mercado Abierto)
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

st.sidebar.info("💡 **Señal para la Siguiente Vela:** La hora de entrada se proyecta automáticamente al inicio del siguiente periodo según la temporalidad seleccionada.")

# 3. Lógica principal del analizador
if st.sidebar.button("🚀 Ejecutar Análisis de Mercado"):
    with st.spinner(f"Procesando datos para {activo}..."):
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
            
            if df.empty or len(df) < 20:
                st.warning("⚠️ No hay suficientes datos disponibles para este intervalo en este momento. Intenta con otra temporalidad.")
            else:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Cálculos de Indicadores Técnicos
                df['EMA_5'] = df['Close'].ewm(span=5, adjust=False).mean()
                df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
                
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                precio_actual = float(df['Close'].iloc[-1])
                ema5_val = float(df['EMA_5'].iloc[-1])
                ema20_val = float(df['EMA_20'].iloc[-1])
                rsi_val = float(df['RSI'].iloc[-1]) if not np.isnan(df['RSI'].iloc[-1]) else 50.0
                
                # --- CALCULO DE HORA UTC-3 Y SIGUIENTE VELA ---
                tz_utc_minus_3 = timezone(timedelta(hours=-3))
                ahora_utc3 = datetime.now(tz_utc_minus_3)
                
                # Mapear la temporalidad a minutos para calcular la hora de la siguiente vela
                minutos_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "1d": 1440}
                minutos_add = minutos_map.get(temporalidad, 1)
                
                # Redondear al siguiente bloque de tiempo de la vela
                # Esto alinea la hora exactamente al cierre de la vela actual / apertura de la siguiente
                segundos_totales = minutos_add * 60
                timestamp_actual = ahora_utc3.timestamp()
                timestamp_siguiente_vela = ((timestamp_actual // segundos_totales) + 1) * segundos_totales
                
                siguiente_vela_dt = datetime.fromtimestamp(timestamp_siguiente_vela, tz_utc_minus_3)
                
                hora_actual_str = ahora_utc3.strftime("%H:%M:%S")
                hora_entrada_str = siguiente_vela_dt.strftime("%H:%M:%S")
                
                # --- MÉTRICAS VISUALES ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Precio Actual", f"{precio_actual:.5f}")
                col2.metric("EMA 5 (Rápida)", f"{ema5_val:.5f}")
                col3.metric("RSI (14)", f"{rsi_val:.2f}")
                col4.metric("Hora Actual (UTC-3)", hora_actual_str)
                
                st.markdown("---")
                
                # --- MOTOR DE DECISIÓN DE SEÑALES ---
                st.subheader(f"🎯 Resultado del Análisis para: {activo}")
                
                razones = []
                if ema5_val > ema20_val:
                    razones.append("La EMA rápida (5) está por encima de la EMA lenta (20) (Tendencia Alcista).")
                else:
                    razones.append("La EMA rápida (5) está por debajo de la EMA lenta (20) (Tendencia Bajista).")
                
                if rsi_val < 30:
                    razones.append(f"El RSI está en niveles de sobreventa ({rsi_val:.1f}), posible rebote al alza.")
                elif rsi_val > 70:
                    razones.append(f"El RSI está en niveles de sobrecompra ({rsi_val:.1f}), posible corrección a la baja.")
                else:
                    razones.append(f"El RSI se encuentra en zona neutral ({rsi_val:.1f}).")
                
                # Mostrar señal indicando la hora exacta de la siguiente vela
                if ema5_val > ema20_val and rsi_val < 65:
                    st.success(f"### 🟢 SEÑAL SUGERIDA: CALL (COMPRA / SUBIR)")
                    st.markdown(f"🕒 **Hora exacta de entrada (Próxima Vela):** `{hora_entrada_str} UTC-3`")
                    st.write(f"Temporalidad de operación: **{temporalidad}**. Prepárate para entrar en cuanto el reloj marque la hora indicada.")
                elif ema5_val < ema20_val and rsi_val > 35:
                    st.error(f"### 🔴 SEÑAL SUGERIDA: PUT (VENTA / BAJAR)")
                    st.markdown(f"🕒 **Hora exacta de entrada (Próxima Vela):** `{hora_entrada_str} UTC-3`")
                    st.write(f"Temporalidad de operación: **{temporalidad}**. Prepárate para entrar en cuanto el reloj marque la hora indicada.")
                else:
                    st.warning(f"### ⚪ MERCADO LATERAL / SIN SEÑAL CLARA")
                    st.write("Los indicadores muestran señales mixtas. Se recomienda esperar mejor confirmación.")
                
                with st.expander("🔍 Ver detalles del análisis técnico"):
                    for r in razones:
                        st.write(f"- {r}")
                
                # --- GRÁFICA VISUAL DE PRECIOS Y MEDIAS ---
                st.markdown("---")
                st.subheader("📊 Gráfica de Comportamiento del Precio")
                
                df_chart = df[['Close', 'EMA_5', 'EMA_20']].tail(50)
                st.line_chart(df_chart)
                
                with st.expander("Ver tabla histórica de datos recientes"):
                    st.dataframe(df[['Close', 'EMA_5', 'EMA_20', 'RSI']].tail(10))

        except Exception as e:
            st.error(f"Ocurrió un error al procesar los datos de mercado: {e}")
else:
    st.info("👈 Selecciona tu activo y temporalidad en la barra lateral y haz clic en **Ejecutar Análisis de Mercado**.")
