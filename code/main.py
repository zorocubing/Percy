import os
import subprocess
import psutil
import pynvml
from pynvml import *

# Try to initialize NVIDIA management library
try:
    nvmlInit()
except NVMLError as e:
    print(f"Oops! Couldn't start Percy - NVIDIA GPU issue: {e}")
    print("Make sure you have an NVIDIA GPU and drivers installed.")
    exit()

# Main loop for Percy
print("Welcome to Percy! I'm your PC agent. Ask away! (Type 'exit' to quit)")
while True:
    # Updated prompt to hint at new command
    command = input("What would you like to know? (Driver Version/GPU Name/GPU Usage): ").lower().strip()

    # Exit condition
    if command == "exit":
        print("Goodbye! Percy out!")
        nvmlShutdown()  # Clean up pynvml
        break

    # Driver Version command
    elif command in ["driver version", "driver", "version"]:
        try:
            driver_version = nvmlSystemGetDriverVersion()
            print(f"Driver Version: {driver_version}")
        except NVMLError as e:
            print(f"Couldn't get driver version: {e}")

    # GPU Name command
    elif command in ["gpu name", "gpu", "name"]:
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

    # GPU Usage command
    elif command in ["gpu usage", "usage", "gpu load"]:
        try:
            device_count = nvmlDeviceGetCount()
            if device_count == 0:
                print("No NVIDIA GPUs found. Can’t check usage!")
            else:
                for i in range(device_count):
                    handle = nvmlDeviceGetHandleByIndex(i)
                    gpu_name = nvmlDeviceGetName(handle)
                    utilization = nvmlDeviceGetUtilizationRates(handle)  # Get usage
                    print(f"GPU {i} ({gpu_name}): {utilization.gpu}% usage")
        except NVMLError as e:
            print(f"Couldn't get GPU usage: {e}")

    # Handle invalid commands (updated hint)
    else:
        print("Huh? I didn’t catch that. Try 'driver version', 'gpu name', or 'gpu usage'. Or 'exit' to quit.")