import paho.mqtt.client as paho
import ssl
import streamlit as st
import matplotlib.pyplot as plt
from collections import deque
import warnings

# Suppress the missing ScriptRunContext warning
warnings.filterwarnings("ignore", message="missing ScriptRunContext! This warning can be ignored when running in bare mode")

# Constants for scaling
scalev = 409.6  # Velocity scale factor
scaleg = 2367.13  # Acceleration scale factor

# Initialize global variables for storing data
sensor_data = {
    'time': deque(maxlen=100),
    'velx': deque(maxlen=100),
    'vely': deque(maxlen=100),
    'velz': deque(maxlen=100),
    'accx': deque(maxlen=100),
    'accy': deque(maxlen=100),
    'accz': deque(maxlen=100),
}

# Callback function when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print(f'Connected to MQTT broker with code {rc}')
    client.subscribe('#', qos=0)

# Callback function when a message is received
def on_message(client, userdata, message):
    payload = message.payload
    buffer = bytearray(payload)

    if len(buffer) >= 18:  # Ensure sufficient data
        int_sensor_id = buffer[2]  # Extract sensor ID

        if int_sensor_id == 245:  # Check for specific sensor ID
            # Extract and convert sensor data
            velx = int.from_bytes(buffer[5:7], byteorder='big', signed=False) / scalev
            vely = int.from_bytes(buffer[7:9], byteorder='big', signed=False) / scalev
            velz = int.from_bytes(buffer[9:11], byteorder='big', signed=False) / scalev
            accx = int.from_bytes(buffer[11:13], byteorder='big', signed=False) / scaleg
            accy = int.from_bytes(buffer[13:15], byteorder='big', signed=False) / scaleg
            accz = int.from_bytes(buffer[15:17], byteorder='big', signed=False) / scaleg

            # Append to global data
            sensor_data['time'].append(len(sensor_data['time']) + 1)
            sensor_data['velx'].append(velx)
            sensor_data['vely'].append(vely)
            sensor_data['velz'].append(velz)
            sensor_data['accx'].append(accx)
            sensor_data['accy'].append(accy)
            sensor_data['accz'].append(accz)

# Streamlit application
st.title("Real-time Sensor Data Visualization")

# Update plot function
def update_plot():
    st.write("### Sensor Data")
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

    st.pyplot(fig)
    plt.close(fig)

# Initialize the MQTT client
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv311)
client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)
client.username_pw_set("test", "12345")
client.connect("3f4b987c21d74a5a87e6bdc7411d5651.s1.eu.hivemq.cloud", 8883)

# Assign callback functions
client.on_connect = on_connect
client.on_message = on_message

# Start the MQTT client loop in the background
client.loop_start()

# Streamlit loop for live plotting
while True:
    update_plot()
    st.experimental_rerun()
