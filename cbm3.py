import paho.mqtt.client as paho
import ssl
import streamlit as st
import matplotlib.pyplot as plt
from collections import deque
import time
#senr = 0

# Constants for scaling
scalev = 409.6  # Velocity scale factor
scaleg = 2367.13  # Acceleration scale factor

# Initialize global variables for storing data
sensor_data = {
    'time': deque(maxlen=100),  # To store time values (timestamps)
    'velx': deque(maxlen=100),  # To store velocity X values
    'vely': deque(maxlen=100),  # To store velocity Y values
    'velz': deque(maxlen=100),  # To store velocity Z values
    'accx': deque(maxlen=100),  # To store acceleration X values
    'accy': deque(maxlen=100),  # To store acceleration Y values
    'accz': deque(maxlen=100),  # To store acceleration Z values
   # 'senr': deque(maxlen=100),
}

# Callback function when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print(f'Connected to MQTT broker with code {rc}')
    client.subscribe('#', qos=0)  # Subscribe to all topics

# Callback function when a message is received
def on_message(client, userdata, message):
    payload = message.payload
    buffer = bytearray(payload)

    # Extract sensor data (assuming specific byte positions for demonstration)
    #int_senr = buffer[2:3] 
    int_velx = buffer[5:7]
    int_vely = buffer[7:9]
    int_velz = buffer[9:11]
    int_accx = buffer[11:13]
    int_accy = buffer[13:15]
    int_accz = buffer[15:17]

    # Convert bytes to integers and scale
   # senr = int.from_bytes(int_senr, byteorder='big', signed=False)
    velx = int.from_bytes(int_velx, byteorder='big', signed=False) / scalev
    vely = int.from_bytes(int_vely, byteorder='big', signed=False) / scalev
    velz = int.from_bytes(int_velz, byteorder='big', signed=False) / scalev
    accx = int.from_bytes(int_accx, byteorder='big', signed=False) / scaleg
    accy = int.from_bytes(int_accy, byteorder='big', signed=False) / scaleg
    accz = int.from_bytes(int_accz, byteorder='big', signed=False) / scaleg


    # Add data to the global deque
    sensor_data['time'].append(time.time())
    sensor_data['velx'].append(velx)
    sensor_data['vely'].append(vely)
    sensor_data['velz'].append(velz)
    sensor_data['accx'].append(accx)
    sensor_data['accy'].append(accy)
    sensor_data['accz'].append(accz)
    #sensor_data['senr'].append(senr)



# MQTT Client setup
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv311)
client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
client.username_pw_set("test", "12345")
client.connect("3f4b987c21d74a5a87e6bdc7411d5651.s1.eu.hivemq.cloud", 8883)
client.on_connect = on_connect
client.on_message = on_message

# Start MQTT loop in a background thread
#client.loop_start()
client.loop_forever(timeout=1.0)

# Streamlit app interface
st.title("Real-time Sensor Data Visualization")
graph_placeholder = st.empty()  # Placeholder for the graph

#if senr == '248':
while True:
    with graph_placeholder.container():
        
        fig, ax = plt.subplots(2, 1, figsize=(10, 6))
        
        # Plot Velocity data
        ax[0].plot(sensor_data['time'], sensor_data['velx'], label='Velocity X')
        ax[0].plot(sensor_data['time'], sensor_data['vely'], label='Velocity Y')
        ax[0].plot(sensor_data['time'], sensor_data['velz'], label='Velocity Z')
        ax[0].set_title('Velocity vs Time')
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Velocity (scaled)')
        ax[0].legend()

        # Plot Acceleration data
        ax[1].plot(sensor_data['time'], sensor_data['accx'], label='Acceleration X')
        ax[1].plot(sensor_data['time'], sensor_data['accy'], label='Acceleration Y')
        ax[1].plot(sensor_data['time'], sensor_data['accz'], label='Acceleration Z')
        ax[1].set_title('Acceleration vs Time')
        ax[1].set_xlabel('Time')
        ax[1].set_ylabel('Acceleration (scaled)')
        ax[1].legend()

        # Render the updated graph
        st.pyplot(fig)
        time.sleep(2)  # Add a small delay for smoother updates
