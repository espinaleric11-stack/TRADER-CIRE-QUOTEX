import time
import pandas as pd
from quotexpy import Quotex  # Librería comunitaria para conectar con Quotex

# 1. Configuración de Credenciales y Activo
# Nota: Es altamente recomendable probar primero en tu cuenta DEMO.
EMAIL = "tu_correo@email.com"
PASSWORD = "tu_contraseña"
ACTIVO = "EURUSD"  # Puedes usar pares normales o con terminación "_otc" para fines de semana
TEMPORALIDAD = 60  # Seguros de 1 minuto (60 segundos) por vela

print("Conectando con Quotex...")
client = Quotex(email=EMAIL, password=PASSWORD)

# Función de inicio de sesión
async def conectar_quotex():
    check, reason = await client.connect()
    if not check:
        print(f"Error al conectar con Quotex: {reason}")
        return False
    print("¡Conexión exitosa a Quotex!")
    return True

# 2. Bucle principal de análisis de señales para Opciones Binarias
async def generar_senales_binarias():
    conectado = await conectar_quotex()
    if not conectado:
        return

    print(f"Analizando el activo {ACTIVO} en Quotex para opciones binarias...")

    while True:
        try:
            # Obtener las últimas velas históricas de la plataforma
            # Quotex trabaja muy de la mano con velas de M1 (60s) o M5 (300s)
            candles = await client.get_candles(ACTIVO, 60) # Últimas velas de 1 min
            
            if not candles:
                print("Esperando datos de velas...")
                await asyncio.sleep(5)
                continue

            df = pd.DataFrame(candles)

            # 3. Calcular Indicadores (Estrategia de Cruce de EMAs rápida y lenta)
            df['EMA_5'] = df['close'].ewm(span=5, adjust=False).mean()
            df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()

            # Tomar los valores de la penúltima y última vela cerrada
            actual_rapida = df['EMA_5'].iloc[-2]
            actual_lenta = df['EMA_20'].iloc[-2]
            anterior_rapida = df['EMA_5'].iloc[-3]
            anterior_lenta = df['EMA_20'].iloc[-3]

            precio_actual = df['close'].iloc[-2]

            # 4. Generación de la Señal de Binarias
            # Cruce alcista -> Opción de COMPRA (CALL / Subir)
            if anterior_rapida <= anterior_lenta and actual_rapida > actual_lenta:
                print(f"\n[🟢 SEÑAL DE COMPRA / CALL EN QUOTEX]")
                print(f"Activo: {ACTIVO} | Precio: {precio_actual}")
                print(f"Acción sugerida: Abrir operación a la ALZA con expiración a 1 o 5 minutos.\n")
                
                # OPCIONAL: Si quisieras ejecución automática (bajo tu propio riesgo), descomenta la línea de abajo:
                # await client.buy(amount=1, asset=ACTIVO, action="call", duration=60)

            # Cruce bajista -> Opción de VENTA (PUT / Bajar)
            elif anterior_rapida >= anterior_lenta and actual_rapida < actual_lenta:
                print(f"\n[🔴 SEÑAL DE VENTA / PUT EN QUOTEX]")
                print(f"Activo: {ACTIVO} | Precio: {precio_actual}")
                print(f"Acción sugerida: Abrir operación a la BAJA con expiración a 1 o 5 minutos.\n")
                
                # OPCIONAL: Ejecución automática
                # await client.buy(amount=1, asset=ACTIVO, action="put", duration=60)

            else:
                print(f"Monitoreando {ACTIVO}... Sin cruce de medias aún.")

            # Esperar a que concluya la vela actual
            await asyncio.sleep(60)

        except Exception as e:
            print(f"Error en el ciclo de análisis: {e}")
            await asyncio.sleep(10)

# Para ejecutar el script asíncrono en Python:
# import asyncio
# asyncio.run(generar_senales_binarias())
