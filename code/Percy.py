import os
import subprocess
import psutil
import pynvml
from pynvml import *
from psutil._common import bytes2human
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread


# Define the pretty-print function for memory
def pprint_ntuple(nt):
    result = []
    for name in nt._fields:
        value = getattr(nt, name)
        if name != 'percent':
            value = bytes2human(value)
        result.append('{:<10} : {:>7}'.format(name.capitalize(), value))
    return '\n'.join(result)


# Initialize speech recognizer
recognizer = sr.Recognizer()


# Function to process speech input
def listen_for_command():
    with sr.Microphone() as source:
        chat_area.insert(tk.END, "Listening for your command...\n")
        chat_area.see(tk.END)
        root.update()
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            text = recognizer.recognize_google(audio).lower().strip()
            chat_area.insert(tk.END, f"You said: {text}\n")
            chat_area.see(tk.END)
            root.update()
            return text
        except sr.UnknownValueError:
            chat_area.insert(tk.END, "Sorry, I couldn’t understand you.\n")
            chat_area.see(tk.END)
            root.update()
            return None
        except sr.RequestError as e:
            chat_area.insert(tk.END, f"Speech recognition error: {e}\n")
            chat_area.see(tk.END)
            root.update()
            return None
        except sr.WaitTimeoutError:
            chat_area.insert(tk.END, "Timed out waiting for speech.\n")
            chat_area.see(tk.END)
            root.update()
            return None


# Function to map text/voice command to action
def process_command(command):
    if not command:
        return False

    # Check for exit first
    if command == "exit":
        chat_area.insert(tk.END, "Goodbye! Percy out!\n")
        chat_area.see(tk.END)
        root.update()
        return True

    # Map voice/text commands to actions
    if command in ["driver version", "driver", "version"]:
        try:
            driver_version = nvmlSystemGetDriverVersion()
            chat_area.insert(tk.END, f"Driver Version: {driver_version}\n")
        except NVMLError as e:
            chat_area.insert(tk.END, f"Couldn't get driver version: {e}\n")

    elif command in ["gpu name", "gpu", "name", "check gpu name"]:
        try:
            device_count = nvmlDeviceGetCount()
            if device_count == 0:
                chat_area.insert(tk.END, "No NVIDIA GPUs found. Are you sure you have an RTX card?\n")
            else:
                for i in range(device_count):
                    handle = nvmlDeviceGetHandleByIndex(i)
                    gpu_name = nvmlDeviceGetName(handle)
                    chat_area.insert(tk.END, f"GPU {i}: {gpu_name}\n")
        except NVMLError as e:
            chat_area.insert(tk.END, f"Couldn't get GPU name: {e}\n")

    elif command in ["gpu usage", "usage", "gpu load", "check gpu usage"]:
        try:
            device_count = nvmlDeviceGetCount()
            if device_count == 0:
                chat_area.insert(tk.END, "No NVIDIA GPUs found. Can’t check usage!\n")
            else:
                for i in range(device_count):
                    handle = nvmlDeviceGetHandleByIndex(i)
                    gpu_name = nvmlDeviceGetName(handle)
                    utilization = nvmlDeviceGetUtilizationRates(handle)
                    chat_area.insert(tk.END, f"GPU {i} ({gpu_name}): {utilization.gpu}% usage\n")
        except NVMLError as e:
            chat_area.insert(tk.END, f"Couldn't get GPU usage: {e}\n")

    elif command in ["cpu", "cpu usage", "cpu load", "check cpu usage"]:
        cpu_usage = psutil.cpu_percent()
        chat_area.insert(tk.END, f"CPU {cpu_usage}% usage\n")

    elif command in ["ram", "ram usage", "memory", "memory usage", "check memory"]:
        chat_area.insert(tk.END, "MEMORY\n------\n")
        chat_area.insert(tk.END, pprint_ntuple(psutil.virtual_memory()) + "\n")

    else:
        chat_area.insert(tk.END,
                         "Huh? I didn’t catch that. Try 'driver version', 'gpu name', 'gpu usage', 'cpu usage', or 'memory'.\n")

    chat_area.see(tk.END)
    root.update()
    return False


# Try to initialize NVIDIA management library
try:
    nvmlInit()
except NVMLError as e:
    print(f"Oops! Couldn't start Percy - NVIDIA GPU issue: {e}")
    print("Make sure you have an NVIDIA GPU and drivers installed.")
    exit()

# Tkinter UI
root = tk.Tk()
root.title("Percy")
root.geometry("500x650")
root.configure(bg="#222325")  # Dark background

# Set window icon
try:
    root.iconbitmap("percy_icon.ico")  # Use ICO for window icon (Windows)
except tk.TclError:
    try:
        icon = tk.PhotoImage(file="percy_icon.png")  # Fallback to PNG (macOS/Linux)
        root.iconphoto(True, icon)
    except tk.TclError as e:
        print(f"Failed to load window icon: {e}")

# Title label
title_label = tk.Label(root, text="Percy", font=("Arial", 16), fg="#D9D9D9", bg="#222325")
title_label.pack(pady=10)

# Chat area (scrollable text)
chat_area = scrolledtext.ScrolledText(root, height=30, width=50, bg="#222325", fg="#FFFFFF", font=("Arial", 12),
                                      wrap=tk.WORD, borderwidth=0)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_area.insert(tk.END, "Welcome to Percy! I'm your PC agent. Speak or type a command.\n")
chat_area.see(tk.END)

# Input frame (text entry + mic button)
input_frame = tk.Frame(root, bg="#222325")
input_frame.pack(fill=tk.X, padx=10, pady=10)


# Text entry
def on_entry_submit(event):
    command = entry.get().lower().strip()
    if command:
        chat_area.insert(tk.END, f"You typed: {command}\n")
        if process_command(command):
            nvmlShutdown()
            root.destroy()
        entry.delete(0, tk.END)


entry = tk.Entry(input_frame, bg="#222325", fg="#D9D9D9", font=("Arial", 12), insertbackground="#FFFFFF", borderwidth=0)
entry.insert(0, "Message Percy")


def on_entry_click(event):
    if entry.get() == "Message Percy":
        entry.delete(0, tk.END)
        entry.config(fg="#FFFFFF")


entry.bind("<FocusIn>", on_entry_click)
entry.bind("<Return>", on_entry_submit)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))


# Mic button with custom icon
def on_mic_click():
    Thread(target=mic_thread).start()


def mic_thread():
    voice_command = listen_for_command()
    if process_command(voice_command):
        nvmlShutdown()
        root.destroy()


try:
    mic_icon = tk.PhotoImage(file="mic_icon.png")  # Load custom mic icon
    mic_button = tk.Button(input_frame, image=mic_icon, bg="#222325", borderwidth=0, command=on_mic_click)
    mic_button.pack(side=tk.RIGHT)
except tk.TclError as e:
    print(f"Failed to load mic icon: {e}")
    mic_button = tk.Button(input_frame, text="🎙️", font=("Arial", 12), bg="#222325", fg="#FFFFFF", borderwidth=0,
                           command=on_mic_click)
    mic_button.pack(side=tk.RIGHT)


# Optional Exit button with custom icon
def on_exit():
    if process_command("exit"):
        nvmlShutdown()
        root.destroy()


try:
    exit_icon = tk.PhotoImage(file="exit_icon.png")  # Load custom exit icon
    exit_button = tk.Button(root, image=exit_icon, bg="#222325", borderwidth=0, command=on_exit)
    exit_button.place(x=500, y=15)  # Top-right corner
except tk.TclError as e:
    # Fallback: Use text-based Exit button
    exit_button = tk.Button(root, text="X", font=("Arial", 12), bg="#FF0000", fg="#FFFFFF", borderwidth=0, command=on_exit)
    exit_button.place(x=450, y=13)

# Start the Tkinter loop
root.mainloop()

# Clean up on exit (in case window is closed manually)
nvmlShutdown()