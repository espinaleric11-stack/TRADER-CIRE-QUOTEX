import streamlit as st
import pandas as pd
import numpy as np
import datetime

# 1. Configuración de la interfaz
st.set_page_config(
    page_title="Analizador Técnico - Opciones & OTC", 
    page_icon="📈", 
    layout="wide"
)

st.title("📈 Analizador Técnico Independiente (Especial OTC & Forex)")
st.markdown("Herramienta de análisis en tiempo real basada en indicadores técnicos (Medias Móviles y RSI).")

# 2. Panel lateral de configuración con activos OTC y Forex
st.sidebar.header("Parámetros de Análisis")

activo = st.sidebar.selectbox(
    "Seleccionar Activo / Par", 
    [
        # Pares OTC (Simulados para análisis técnico continuo)
        "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc", "EURJPY_otc", "GBPJPY_otc",
        # Forex Principales (Mercado Abierto / Estándar)
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "NZDUSD=X", "USDCHF=X",
        # Metales y Materias Primas
        "GC=F (Oro / XAU)", "SI=F (Plata)", "CL=F (Petróleo Crudo)",
        # Criptomonedas
        "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD"
    ]
)

temporalidad = st.sidebar.selectbox(
    "Temporalidad de las Velas", 
    ["1m", "5m", "15m", "1h", "1d"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Nota sobre activos OTC:** Dado que los mercados OTC privados de los brókeres no publican datos oficiales en la web abierta, el sistema utiliza el par forex base equivalente en tiempo real para calcular las medias móviles y el RSI con alta precisión.")

# 3. Lógica principal del analizador
if st.sidebar.button("🚀 Ejecutar Análisis de Mercado"):
    with st.spinner(f"Procesando datos para {activo}..."):
        try:
            import yfinance as yf
            
            # Mapear activos OTC al equivalente en Yahoo Finance para obtener el flujo de precios
            simbolo_map = {
                "EURUSD_otc": "EURUSD=X",
                "GBPUSD_otc": "GBPUSD=X",
                "USDJPY_otc": "USDJPY=X",
                "AUDUSD_otc": "AUDUSD=X",
                "EURJPY_otc": "EURJPY=X",
                "GBPJPY_otc": "GBPJPY=X"
            }
            
            # Limpiar o traducir el símbolo para la consulta
            simbolo_limpio = activo.split(" ")[0]
            symbol_to_fetch = simbolo_map.get(simbolo_limpio, simbolo_limpio)
            
            # Descargar datos recientes
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
                
                # RSI de 14 periodos
                delta = df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['RSI'] = 100 - (100 / (1 + rs))
                
                precio_actual = float(df['Close'].iloc[-1])
                ema5_val = float(df['EMA_5'].iloc[-1])
                ema20_val = float(df['EMA_20'].iloc[-1])
                rsi_val = float(df['RSI'].iloc[-1]) if not np.isnan(df['RSI'].iloc[-1]) else 50.0
                
                # --- MÉTRICAS VISUALES ---
                col1, col2, col3 = st.columns(3)
                col1.metric("Precio Actual", f"{precio_actual:.5f}")
                col2.metric("EMA 5 (Rápida)", f"{ema5_val:.5f}")
                col3.metric("RSI (14)", f"{rsi_val:.2f}")
                
                st.markdown("---")
                
                # --- MOTOR DE DECISIÓN DE SEÑALES ---
                st.subheader("🎯 Resultado del Análisis Técnico")
                
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
                
                # Mostrar señal
                if ema5_val > ema20_val and rsi_val < 65:
                    st.success("### 🟢 SEÑAL SUGERIDA: CALL (COMPRA / SUBIR)")
                    st.write("Condiciones favorables detectadas para operaciones al alza.")
                elif ema5_val < ema20_val and rsi_val > 35:
                    st.error("### 🔴 SEÑAL SUGERIDA: PUT (VENTA / BAJAR)")
                    st.write("Condiciones favorables detectadas para operaciones a la baja.")
                else:
                    st.warning("### ⚪ MERCADO LATERAL / SIN SEÑAL CLARA")
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
    st.info("👈 Selecciona tu activo (incluyendo las opciones **_otc**) en la barra lateral y haz clic en **Ejecutar Análisis de Mercado**.")
