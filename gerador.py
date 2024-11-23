import paho.mqtt.client as mqtt
import requests
import json
import random
import time

# Configurações do Mosquitto
LOCAL_BROKER = "localhost"
LOCAL_PORT = 1883
LOCAL_TOPIC = "sensor1/temperature"

# Configurações do Tago.io
DEVICE_TOKEN = "01791964-bb94-4334-ad5b-2d1271f288d0"
TAGO_URL = "https://api.tago.io/data"

# Função para gerar dados simulados aleatórios
def generate_random_data():
    temperature = round(random.uniform(-10, 45), 2)  # Temperatura irreal: -10°C a 45°C
    humidity = round(random.uniform(-5, 110), 2)    # Umidade irreal: -5% a 110%
    noise = round(random.uniform(-10, 110), 2)      # Barulho irreal: -10 dB a 110 dB
    light = round(random.uniform(0, 1800), 2)       # Luz irreal: 0 a 1800 lumens

    return {
        "temperature": temperature,
        "humidity": humidity,
        "noise": noise,
        "light": light
    }

# Função para verificar outliers
def check_for_outliers(data):
    if data["temperature"] < -5 or data["temperature"] > 40:
        return False     # Outlier na temperatura

    if data["humidity"] < 0 or data["humidity"] > 100:
        return False    # Outlier na umidade

    if data["noise"] < 0 or data["noise"] > 100:
        return False    # Outlier no barulho

    if data["light"] < 0 or data["light"] > 1500:
        return False    # Outlier na luz

    return True    # Dados válidos (não são outliers)

# Função para enviar os dados ao Tago.io via HTTP
def send_data_to_tago(data):
    payload = [
        {"variable": "temperature", "value": data["temperature"]},
        {"variable": "humidity", "value": data["humidity"]},
        {"variable": "noise", "value": data["noise"]},
        {"variable": "light", "value": data["light"]}
    ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": DEVICE_TOKEN
    }

    # Envia os dados ao Tago.io
    response = requests.post(TAGO_URL, headers=headers, json=payload)

    # Verifica a resposta do Tago.io
    if response.status_code == 200 or response.status_code == 202:
        print(f"Dados enviados ao Tago.io com sucesso: {payload}")
    else:
        print(f"Erro ao enviar dados: {response.status_code} - {response.text}")

# Callback para processar mensagens do Mosquitto (não é necessário se apenas enviar dados aleatórios)
def on_message(client, userdata, msg):
    pass  # Não precisamos de uma implementação para isso, pois estamos enviando dados automaticamente

# Função principal do script
def main():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(LOCAL_BROKER, LOCAL_PORT, 60)
    client.subscribe(LOCAL_TOPIC)

    client.loop_start()

    try:
        while True:
            # Gerar dados aleatórios
            data = generate_random_data()
            print(f"Gerando dados aleatórios: {data}")

            # Verificar se os dados são outliers
            if check_for_outliers(data):
                # Enviar dados válidos ao Tago.io
                send_data_to_tago(data)
            else:
                print(f"Outlier detectado, dados não enviados: {data}")

            # Aguarda 3 segundos antes de gerar e enviar novamente
            time.sleep(3)

    except KeyboardInterrupt:
        print("Interrompendo o script...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
