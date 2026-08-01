import sys
import types

# -------------------------------------------------------------
# PARCHE GLOBAL CRÍTICO PARA DISTUTILS.VERSION (Python 3.12+)
# -------------------------------------------------------------
class LooseVersion:
    def __init__(self, vstring=None):
        self.vstring = vstring
        self.version = [int(x) for x in vstring.split(".") if x.isdigit()] if vstring else []
        
    def __str__(self):
        return self.vstring or ""
    def __repr__(self):
        return f"LooseVersion ('{self.vstring}')"
    def _cmp(self, other):
        if isinstance(other, LooseVersion):
            other_v = other.version
        else:
            other_v = [int(x) for x in str(other).split(".") if x.isdigit()]
        
        if self.version == other_v:
            return 0
        elif self.version < other_v:
            return -1
        else:
            return 1

    def __lt__(self, other): return self._cmp(other) < 0
    def __le__(self, other): return self._cmp(other) <= 0
    def __gt__(self, other): return self._cmp(other) > 0
    def __ge__(self, other): return self._cmp(other) >= 0
    def __eq__(self, other): return self._cmp(other) == 0
    def __ne__(self, other): return self._cmp(other) != 0

# Forzar el módulo en el sistema antes de que cualquier librería lo requiera
distutils_mod = types.ModuleType("distutils")
distutils_version = types.ModuleType("distutils.version")
distutils_version.LooseVersion = LooseVersion
distutils_mod.version = distutils_version

sys.modules["distutils"] = distutils_mod
sys.modules["distutils.version"] = distutils_version
# -------------------------------------------------------------

import streamlit as st
import asyncio
import pandas as pd

# Configuración visual de la interfaz
st.set_page_config(page_title="Señales Quotex", page_icon="📈", layout="centered")

st.title("📈 Generador de Señales - Quotex")
st.write("Conéctate para analizar el mercado de opciones binarias en tiempo real.")

# Panel lateral para credenciales y parámetros
st.sidebar.header("Configuración de Cuenta")
email = st.sidebar.text_input("Correo de Quotex")
password = st.sidebar.text_input("Contraseña", type="password", value="")
activo = st.sidebar.selectbox("Activo a operar", ["EURUSD", "GBPUSD", "EURUSD_otc", "XAUUSD_otc"])

# Inicializar variables de estado
if "conectado" not in st.session_state:
    st.session_state.conectado = False

# Lógica de conexión segura
if st.sidebar.button("Conectar al Bróker"):
    if not email or not password:
        st.warning("⚠️ Por favor ingresa tu correo y contraseña en la barra lateral.")
    else:
        with st.spinner("🔄 Conectando con Quotex (iniciando navegador oculto)..."):
            
            async def test_conexion():
                try:
                    from quotexpy import Quotex
                    client = Quotex(email=email, password=password)
                    check, reason = await client.connect()
                    return check, reason, client
                except Exception as e:
                    return False, str(e), None

            exito, mensaje, cliente_quotex = asyncio.run(test_conexion())

            if exito:
                st.session_state.conectado = True
                st.session_state.client = cliente_quotex
                st.success("¡Conexión establecida con éxito!")
            else:
                st.error(f"❌ Error al conectar: {mensaje}")

# Panel principal una vez conectado
if st.session_state.get("conectado", False):
    st.info(f"🟢 Sesión activa para el activo: **{activo}**")
    
    if st.button("📊 Analizar Mercado y Obtener Velas"):
        with st.spinner("Analizando velas recientes..."):
            
            async def obtener_datos():
                try:
                    client = st.session_state.client
                    candles = await client.get_candles(activo, 60)
                    return candles
                except Exception as e:
                    return None

            candles_data = asyncio.run(obtener_datos())

            if candles_data:
                df = pd.DataFrame(candles_data)
                
                df['EMA_5'] = df['close'].ewm(span=5, adjust=False).mean()
                df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
                
                precio_actual = df['close'].iloc[-2]
                ema5_val = df['EMA_5'].iloc[-2]
                ema20_val = df['EMA_20'].iloc[-2]
                
                st.write(f"**Precio actual del activo:** {precio_actual}")
                
                if ema5_val > ema20_val:
                    st.markdown("### 🟢 SEÑAL SUGERIDA: **CALL (COMPRA / SUBIR)**")
                    st.info("La media rápida está por encima de la lenta.")
                else:
                    st.markdown("### 🔴 SEÑAL SUGERIDA: **PUT (VENTA / BAJAR)**")
                    st.warning("La media rápida está por debajo de la lenta.")
                
                with st.expander("Ver histórico de precios recientes"):
                    st.dataframe(df[['time', 'close', 'EMA_5', 'EMA_20']].tail(10))
            else:
                st.error("No se pudieron recuperar los datos de las velas para este activo.")
