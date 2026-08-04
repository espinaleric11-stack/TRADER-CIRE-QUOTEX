from datetime import datetime, timedelta, timezone
import time
import numpy as np
import pandas as pd
import streamlit as st

# 1. Configuración de la interfaz optimizada para móviles
st.set_page_config(
    page_title="CyberTrader // Quotex Master Signal Radar",
    page_icon="⚡",
    layout="wide",
)

# 2. Inyectar Estilos CSS Adaptativos (Mobile & Desktop)
st.markdown(
    """
<style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #111422 0%, #08090d 100%);
        color: #e0e6ed;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
    }
    .cyber-header {
        background: linear-gradient(135deg, rgba(18, 20, 32, 0.9) 0%, rgba(26, 29, 45, 0.9) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        gap: 10px;
    }
    .cyber-logo {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .cyber-icon {
        font-size: 24px;
        filter: drop-shadow(0 0 10px rgba(0, 255, 204, 0.6));
    }
    .cyber-title-text {
        font-size: 18px;
        font-weight: 900;
        letter-spacing: 1px;
        color: #00ffcc;
        text-shadow: 0 0 12px rgba(0, 255, 204, 0.5);
        margin: 0;
    }
    .cyber-subtitle {
        font-size: 10px;
        color: #8a99ad;
        letter-spacing: 0.5px;
        margin: 0;
        text-transform: uppercase;
    }
    .badge-container {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
    }
    .clock-badge {
        background: rgba(255, 170, 0, 0.1);
        border: 1px solid rgba(255, 170, 0, 0.5);
        color: #ffaa00;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
    }
    .utc-badge {
        background: rgba(0, 255, 204, 0.1);
        border: 1px solid rgba(0, 255, 204, 0.5);
        color: #00ffcc;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
    }
    .asset-card-active {
        background: rgba(0, 255, 128, 0.08);
        border: 2px solid #00ff80;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 0 20px rgba(0, 255, 128, 0.2);
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
        padding: 0.6rem 1.2rem;
        width: 100%;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.95;
        box-shadow: 0 0 25px rgba(0, 255, 204, 0.8);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Inicializar memoria de sesión
if "historial_app" not in st.session_state:
  st.session_state.historial_app = []
if "modo_automatico" not in st.session_state:
  st.session_state.modo_automatico = False
if "ultimos_resultados_globales" not in st.session_state:
  st.session_state.ultimos_resultados_globales = {}

# Obtener hora actual del mercado en UTC-3
tz_utc_minus_3 = timezone(timedelta(hours=-3))
hora_actual_mercado = datetime.now(tz_utc_minus_3).strftime("%H:%M")

# Cabecera adaptable
st.markdown(
    f"""
<div class="cyber-header">
    <div class="cyber-logo">
        <span class="cyber-icon">⚡</span>
        <div>
            <p class="cyber-title-text">CYBER-TRADER MOBILE RADAR</p>
            <p class="cyber-subtitle">Escáner Multi-Nivel Simultáneo (OTC)</p>
        </div>
    </div>
    <div class="badge-container">
        <div class="clock-badge">🕒 {hora_actual_mercado}</div>
        <div class="utc-badge">🌐 UTC-3</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Lista completa de Activos OTC
activos_quotex = {
    "EUR/USD (OTC)": {"symbol": "EURUSD=X", "profit": "82%"},
    "GBP/USD (OTC)": {"symbol": "GBPUSD=X", "profit": "85%"},
    "USD/CAD (OTC)": {"symbol": "USDCAD=X", "profit": "84%"},
    "USD/JPY (OTC)": {"symbol": "USDJPY=X", "profit": "80%"},
    "AUD/USD (OTC)": {"symbol": "AUDUSD=X", "profit": "83%"},
    "EUR/JPY (OTC)": {"symbol": "EURJPY=X", "profit": "81%"},
    "GBP/JPY (OTC)": {"symbol": "GBPJPY=X", "profit": "78%"},
    "EUR/GBP (OTC)": {"symbol": "EURGBP=X", "profit": "84%"},
    "AUD/CAD (OTC)": {"symbol": "AUDCAD=X", "profit": "80%"},
    "NZD/USD (OTC)": {"symbol": "NZDUSD=X", "profit": "79%"},
    "USD/MXN (OTC)": {"symbol": "USDJPY=X", "profit": "84%"},
    "CHF/JPY (OTC)": {"symbol": "CHFJPY=X", "profit": "79%"},
    "EUR/AUD (OTC)": {"symbol": "EURAUD=X", "profit": "81%"},
    "CAD/JPY (OTC)": {"symbol": "CADJPY=X", "profit": "82%"},
    "GBP/AUD (OTC)": {"symbol": "GBPAUD=X", "profit": "83%"},
    "USD/CHF (OTC)": {"symbol": "USDCHF=X", "profit": "80%"},
    "EUR/CHF (OTC)": {"symbol": "EURCHF=X", "profit": "78%"},
    "AUD/NZD (OTC)": {"symbol": "AUDNZD=X", "profit": "79%"},
    "NZD/JPY (OTC)": {"symbol": "NZDJPY=X", "profit": "77%"},
    "XAU/USD (Oro / OTC)": {"symbol": "GC=F", "profit": "88%"},
}

# --- PANEL LATERAL SIMPLIFICADO PARA MÓVIL ---
st.sidebar.header("⚙️ Controles del Sistema")

opcion_temporalidad = st.sidebar.selectbox(
    "Temporalidad de las Velas",
    ["🌐 Todas (Multi-TF)", "1m", "5m", "15m", "1h"],
)

intervalo_escaneo = st.sidebar.slider(
    "Frecuencia de escaneo (segundos)", 10, 60, 10
)

st.sidebar.markdown("---")
col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
  if st.button("🟢 INICIAR"):
    st.session_state.modo_automatico = True
with col_b2:
  if st.button("🔴 DETENER"):
    st.session_state.modo_automatico = False

if st.sidebar.button("🗑️ Limpiar Historial"):
  st.session_state.historial_app = []
  st.sidebar.success("¡Historial reiniciado!")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Estado:** "
    + (
        "🟢 ESCANEANDO 3 NIVELES"
        if st.session_state.modo_automatico
        else "⏸️ EN ESPERA"
    )
)


# Función de escaneo masivo evaluando los 3 niveles simultáneamente
def escanear_todos_los_activos():
  import yfinance as yf

  with st.spinner(
      "🔍 Escaneando mercados y validando los 3 niveles en paralelo..."
  ):
    ahora_utc3 = datetime.now(tz_utc_minus_3)
    hora_actual_str = ahora_utc3.strftime("%H:%M:%S")

    if "Todas" in opcion_temporalidad:
      lista_temporalidades = ["1m", "5m", "15m", "1h"]
    else:
      lista_temporalidades = [opcion_temporalidad]

    resultados_temporales = {}
    niveles_config = {
        "🛡️ Conservador": {"rsi_c": 32, "rsi_p": 68, "atr_m": 0.15},
        "⚖️ Moderado": {"rsi_c": 37, "rsi_p": 63, "atr_m": 0.30},
        "🚀 Agresivo": {"rsi_c": 42, "rsi_p": 58, "atr_m": 0.45},
    }

    for nombre_activo, data in activos_quotex.items():
      symbol = data["symbol"]
      for temp in lista_temporalidades:
        try:
          periodo = "1d" if temp in ["1m", "5m", "15m"] else "5d"
          df = yf.download(
              symbol, period=periodo, interval=temp, progress=False
          )

          if df.empty or len(df) < 30:
            continue

          if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

          minutos_map = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}
          minutos_add = minutos_map.get(temp, 1)
          segundos_totales = minutos_add * 60
          timestamp_siguiente_vela = (
              (ahora_utc3.timestamp() // segundos_totales) + 1
          ) * segundos_totales
          siguiente_vela_dt = datetime.fromtimestamp(
              timestamp_siguiente_vela, tz_utc_minus_3
          )
          hora_entrada_str = siguiente_vela_dt.strftime("%H:%M:%S")

          df["EMA_5"] = df["Close"].ewm(span=5, adjust=False).mean()
          df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

          delta = df["Close"].diff()
          gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
          loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
          rs = gain / loss
          df["RSI"] = 100 - (100 / (1 + rs))

          df["BB_Middle"] = df["Close"].rolling(window=20).mean()
          bb_std = df["Close"].rolling(window=20).std()
          df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
          df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)

          high_low = df["High"] - df["Low"]
          high_close = np.abs(df["High"] - df["Close"].shift())
          low_close = np.abs(df["Low"] - df["Close"].shift())
          true_range = pd.concat(
              [high_low, high_close, low_close], axis=1
          ).max(axis=1)
          df["ATR"] = true_range.rolling(window=14).mean()

          precio_actual = float(df["Close"].iloc[-1])
          precio_anterior = float(df["Close"].iloc[-2])
          ema5_val = float(df["EMA_5"].iloc[-1])
          ema20_val = float(df["EMA_20"].iloc[-1])
          rsi_val = (
              float(df["RSI"].iloc[-1])
              if not np.isnan(df["RSI"].iloc[-1])
              else 50.0
          )
          bb_lower = float(df["BB_Lower"].iloc[-1])
          bb_upper = float(df["BB_Upper"].iloc[-1])
          atr_val = (
              float(df["ATR"].iloc[-1])
              if not np.isnan(df["ATR"].iloc[-1])
              else 0.0
          )

          # Evaluar los 3 niveles de estricción simultáneamente
          for nombre_nivel, params in niveles_config.items():
            c_call = (
                (ema5_val > ema20_val)
                and (rsi_val <= params["rsi_c"])
                and (precio_actual <= (bb_lower + (atr_val * params["atr_m"])))
                and (precio_actual > precio_anterior)
            )
            c_put = (
                (ema5_val < ema20_val)
                and (rsi_val >= params["rsi_p"])
                and (precio_actual >= (bb_upper - (atr_val * params["atr_m"])))
                and (precio_actual < precio_anterior)
            )

            senal = "ARRIBA 🟢" if c_call else ("ABAJO 🔴" if c_put else None)

            if senal:
              clave_resultado = f"{nombre_activo} [{temp}] - {nombre_nivel}"
              info_senal = {
                  "activo_base": nombre_activo,
                  "precio": precio_actual,
                  "rsi": rsi_val,
                  "senal": senal,
                  "entrada": hora_entrada_str,
                  "temporalidad": temp,
                  "nivel": nombre_nivel,
                  "profit": data["profit"],
                  "symbol": symbol,
                  "timestamp": timestamp_siguiente_vela,
              }
              resultados_temporales[clave_resultado] = info_senal

              id_reg = f"{nombre_activo}-{temp}-{nombre_nivel}-{hora_entrada_str}-{senal}"
              if not any(
                  s.get("id") == id_reg for s in st.session_state.historial_app
              ):
                st.session_state.historial_app.append({
                    "id": id_reg,
                    "Hora": hora_actual_str,
                    "Activo": f"{nombre_activo} ({temp})",
                    "Nivel": nombre_nivel,
                    "Señal": senal,
                    "Entrada": hora_entrada_str,
                    "Resultado": "PENDIENTE ⏳",
                    "timestamp_entrada": timestamp_siguiente_vela,
                    "precio_entrada": precio_actual,
                    "symbol_ref": symbol,
                })

        except Exception:
          pass

    st.session_state.ultimos_resultados_globales = resultados_temporales


if (
    st.session_state.modo_automatico
    or not st.session_state.ultimos_resultados_globales
):
  escanear_todos_los_activos()

# --- ACTUALIZAR PENDIENTES DEL HISTORIAL ---
ahora_ts = datetime.now(tz_utc_minus_3).timestamp()

for item in st.session_state.historial_app:
  if item["Resultado"] == "PENDIENTE ⏳":
    if ahora_ts >= item["timestamp_entrada"]:
      try:
        import yfinance as yf

        sim_df = yf.download(
            item["symbol_ref"], period="1d", interval="1m", progress=False
        )
        if not sim_df.empty:
          if isinstance(sim_df.columns, pd.MultiIndex):
            sim_df.columns = sim_df.columns.get_level_values(0)
          precio_final = float(sim_df["Close"].iloc[-1])
          p_entrada = item["precio_entrada"]
          if "ARRIBA" in item["Señal"]:
            item["Resultado"] = (
                "WIN 🟢" if precio_final > p_entrada else "LOSS 🔴"
            )
          else:
            item["Resultado"] = (
                "WIN 🟢" if precio_final < p_entrada else "LOSS 🔴"
            )
      except:
        pass

# --- PANEL VISUAL PRINCIPAL ---
if st.session_state.modo_automatico:
  st.success("🟢 **Modo Automático**: Escaneando los 3 niveles simultáneamente.")

st.subheader("🎯 Señales Detectadas (Multi-Nivel)")

resultados_activos = st.session_state.ultimos_resultados_globales

if resultados_activos:
  cols = st.columns(1 if len(resultados_activos) == 1 else 2)
  idx = 0
  for clave_res, info in resultados_activos.items():
    with cols[idx % len(cols)]:
      st.markdown(
          f"""
            <div class="asset-card-active">
                <h3 style="margin:0; color:#00ffcc; font-size: 15px;">⚡ {info['activo_base']} [{info['temporalidad']}]</h3>
                <p style="margin:4px 0; font-size:12px; color:#ffaa00;">Nivel: <b>{info['nivel']}</b> | Payout: <b>{info['profit']}</b></p>
                <p style="margin:2px 0; font-size:12px; color:#a0aec0;">RSI: <b>{info['rsi']:.1f}</b> | Precio: <b>{info['precio']:.4f}</b></p>
                <hr style="margin:6px 0; border-color:rgba(0,255,128,0.3);">
                <p style="margin:4px 0; font-size:16px;">Señal: <b style="color:{'#00ff80' if 'ARRIBA' in info['senal'] else '#ff4b4b'};">{info['senal']}</b></p>
                <p style="margin:0; font-size:12px; color:#ffffff;">🕒 Entrada: <b>{info['entrada']}</b></p>
            </div>
            """,
          unsafe_allow_html=True,
      )
    idx += 1
else:
  st.info(
      "🔍 Escaneando activos en los 3 niveles de estricción... Las alertas"
      " aparecerán aquí en tiempo real."
  )

st.markdown("---")
st.subheader("📜 Historial de Señales")
if len(st.session_state.historial_app) > 0:
  df_hist = pd.DataFrame(st.session_state.historial_app)[
      ["Hora", "Activo", "Nivel", "Señal", "Entrada", "Resultado"]
  ]
  st.dataframe(df_hist.iloc[::-1], use_container_width=True)
else:
  st.info("Aún no hay operaciones registradas.")

# Bucle automático en tiempo real
if st.session_state.modo_automatico:
  time.sleep(intervalo_escaneo)
  st.rerun()
