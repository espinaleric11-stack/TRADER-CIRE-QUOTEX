import streamlit as st
import asyncio

st.title("Señales Quotex Cloud")

# Crear campos en la interfaz para no quemar credenciales en el código
email = st.sidebar.text_input("Correo de Quotex")
password = st.sidebar.text_input("Contraseña", type="password")
activo = st.sidebar.selectbox("Activo", ["EURUSD", "GBPUSD", "XAUUSD_otc"])

if st.sidebar.button("Conectar y Analizar"):
    if not email or not password:
        st.warning("Por favor ingresa tus credenciales.")
    else:
        st.info("Intentando conectar con el servidor...")
        
        # Función asíncrona segura dentro de Streamlit
        async def ejecutar_conexion():
            try:
                # Importación dentro del botón para evitar bloqueos al cargar la app
                from quotexpy import Quotex
                client = Quotex(email=email, password=password)
                check, reason = await client.connect()
                
                if check:
                    st.success("¡Conexión exitosa!")
                    # Aquí puedes colocar la lógica para obtener velas
                    candles = await client.get_candles(activo, 60)
                    st.write(f"Datos obtenidos correctamente para {activo}")
                else:
                    st.error(f"Fallo al conectar: {reason}")
            except Exception as e:
                st.error(f"Ocurrió un error crítico: {e}")

        # Ejecutar la corrutina en Streamlit
        asyncio.run(ejecutar_conexion())
