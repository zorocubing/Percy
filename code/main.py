import os
import subprocess
import psutil
import pynvml
from pynvml import *
from psutil._common import bytes2human
import speech_recognition as sr

# Define the pretty-print function for memory
def pprint_ntuple(nt):
    for name in nt._fields:
        value = getattr(nt, name)
        if name != 'percent':
            value = bytes2human(value)
        print('{:<10} : {:>7}'.format(name.capitalize(), value))

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Function to process speech input
def listen_for_command():
    with sr.Microphone() as source:
        print("Listening for your command...")
        # Adjust for ambient noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)  # Listen with timeout
            text = recognizer.recognize_google(audio).lower().strip()  # Transcribe with Google API
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn’t understand you.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("Timed out waiting for speech.")
            return None

# Function to map text/voice command to action
def process_command(command):
    if not command:
        return False

        # Check for exit first
    if command == "exit":
        print("Goodbye! Percy out!")
        return True  # Signal to exit

    # Map voice/text commands to actions
    if command in ["driver version", "driver", "version"]:
        try:
            driver_version = nvmlSystemGetDriverVersion()
            print(f"Driver Version: {driver_version}")
        except NVMLError as e:
            print(f"Couldn't get driver version: {e}")

    elif command in ["gpu name", "gpu", "name", "check gpu name"]:
        try:
            device_count = nvmlDeviceGetCount()
            if device_count == 0:
                print("No NVIDIA GPUs found. Are you sure you have an RTX card?")
            else:
                for i in range(device_count):
                    handle = nvmlDeviceGetHandleByIndex(i)
                    gpu_name = nvmlDeviceGetName(handle)
                    print(f"GPU {i}: {gpu_name}")
        except NVMLError as e:
            print(f"Couldn't get GPU name: {e}")

    elif command in ["gpu usage", "usage", "gpu load", "check gpu usage"]:
        try:
            device_count = nvmlDeviceGetCount()
            if device_count == 0:
                print("No NVIDIA GPUs found. Can’t check usage!")
            else:
                for i in range(device_count):
                    handle = nvmlDeviceGetHandleByIndex(i)
                    gpu_name = nvmlDeviceGetName(handle)
                    utilization = nvmlDeviceGetUtilizationRates(handle)
                    print(f"GPU {i} ({gpu_name}): {utilization.gpu}% usage")
        except NVMLError as e:
            print(f"Couldn't get GPU usage: {e}")

    elif command in ["cpu", "cpu usage", "cpu load", "check cpu usage"]:
        cpu_usage = psutil.cpu_percent()
        print(f"CPU {cpu_usage}% usage")

    elif command in ["ram", "ram usage", "memory", "memory usage", "check memory"]:
        print('MEMORY\n------')
        pprint_ntuple(psutil.virtual_memory())

    else:
        print("Huh? I didn’t catch that. Try 'driver version', 'gpu name', 'gpu usage', 'cpu usage', or 'memory'.")
    return False

# Try to initialize NVIDIA management library
try:
    nvmlInit()
except NVMLError as e:
    print(f"Oops! Couldn't start Percy - NVIDIA GPU issue: {e}")
    print("Make sure you have an NVIDIA GPU and drivers installed.")
    exit()

# Main loop for Percy
print("Welcome to Percy! I'm your PC agent. Ask away! (Type 'exit' to quit, 'voice' to use speech)")
while True:
    command = input("What would you like to know? (voice/exit/Driver Version/GPU Name/GPU Usage/CPU Usage/Memory): ").lower().strip()

    # Exit condition for typed input
    if command == "exit":
        print("Goodbye! Percy out!")
        nvmlShutdown()  # Clean up pynvml
        break

    # Voice command trigger
    elif command == "voice":
        voice_command = listen_for_command()
        if process_command(voice_command):  # Check if exit was triggered
            nvmlShutdown()
            break

    # Process text commands directly
    else:
        if process_command(command):
            nvmlShutdown()
            break