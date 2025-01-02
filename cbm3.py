pip install paho-mqtt
import paho.mqtt.client as paho
import ssl
import streamlit as st
import matplotlib.pyplot as plt
from collections import deque
import numpy as np

# Constants for scaling
scalev = 409.6  # Velocity scale factor
scaleg = 2367.13  # Acceleration scale factor

# Initialize global variables for storing data
sensor_data = {
    'time': deque(maxlen=100),    # To store time values (timestamps)
    'velx': deque(maxlen=100),    # To store velocity X values
    'vely': deque(maxlen=100),    # To store velocity Y values
    'velz': deque(maxlen=100),    # To store velocity Z values
    'accx': deque(maxlen=100),    # To store acceleration X values
    'accy': deque(maxlen=100),    # To store acceleration Y values
    'accz': deque(maxlen=100),    # To store acceleration Z values
}

# Callback function when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print('CONNACK received with code %d.' % (rc))
    client.subscribe('#', qos=0)  # Subscribe to all topics

# Callback function when a message is received
def on_message(client, userdata, message):
    payload = message.payload
    buffer = bytearray(payload)

    # Extract sensor data (for demonstration, we assume specific byte positions)
    int_velx = buffer[5:7]
    int_vely = buffer[7:9]
    int_velz = buffer[9:11]

    int_accx = buffer[11:13]
    int_accy = buffer[13:15]
    int_accz = buffer[15:17]

    # Convert bytes to integers
    velxconvert_int = int.from_bytes(int_velx, byteorder='big', signed=False) / scalev
    velyconvert_int = int.from_bytes(int_vely, byteorder='big', signed=False) / scalev
    velzconvert_int = int.from_bytes(int_velz, byteorder='big', signed=False) / scalev

    accxconvert_int = int.from_bytes(int_accx, byteorder='big', signed=False) / scaleg
    accyconvert_int = int.from_bytes(int_accy, byteorder='big', signed=False) / scaleg
    acczconvert_int = int.from_bytes(int_accz, byteorder='big', signed=False) / scaleg

    # Add the received data to the global list (using time as a simple counter here)
    sensor_data['time'].append(len(sensor_data['time']) + 1)  # Simulating time as a counter
    sensor_data['velx'].append(velxconvert_int)
    sensor_data['vely'].append(velyconvert_int)
    sensor_data['velz'].append(velzconvert_int)
    sensor_data['accx'].append(accxconvert_int)
    sensor_data['accy'].append(accyconvert_int)
    sensor_data['accz'].append(acczconvert_int)

    # Update the Streamlit plot
    update_plot()

# Function to update the plot on Streamlit
def update_plot():
    # Create the plot in Streamlit
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

# Initialize the MQTT client
client = paho.Client("123")  # Use a simple client ID
client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)  # TLS settings
client.username_pw_set("test", "12345")  # Username and password

# Assign callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT broker
client.connect("3f4b987c21d74a5a87e6bdc7411d5651.s1.eu.hivemq.cloud", 8883)

# Start the MQTT loop in the background
client.loop_start()

# Create a Streamlit app interface
st.title("Real-time Sensor Data Visualization")

# Streamlit loop to continuously update data
while True:
    # Streamlit will automatically rerun this script every time it updates
    # In case of real-time updates, it automatically renders the plot with the new data
    pass
