import os
import subprocess
import psutil
import pynvml
from pynvml import *

# Initializing the module
nvmlInit()

# Which command would the user want to use
command = input("Welcome to RTX Percy! Ask what you would like to know! (Driver Version/GPU Name): ").lower().strip()

# Driver Version command
if command == "driver version":
    print(f"Driver Version: {nvmlSystemGetDriverVersion()}")

# GPU Name command
elif command == "gpu name":
    deviceCount = nvmlDeviceGetCount()
    for i in range(deviceCount):
        handle = nvmlDeviceGetHandleByIndex(i)
        print(f"GPU Name {i} : {nvmlDeviceGetName(handle)}")

# Syntax Error
else:
    print("Syntax Error")
