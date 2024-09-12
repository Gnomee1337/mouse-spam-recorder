import tkinter as tk
from tkinter import ttk
import subprocess
import time
import threading
import csv
import os
import pyautogui
import keyboard
from tkinter import filedialog, messagebox
import ttkbootstrap as ttkb

# List to store parsed mouse movements and clicks
movements = []

# Global variable to control replay cancellation
cancel_replay = False


# Function to start MouseInfo via command line
def start_mouseinfo():
    status_label.config(text="MouseInfo opened. Record movements and save the log using F1-F6.")
    subprocess.Popen(['py', '-m', 'mouseinfo'])


def load_log():
    global movements
    file_path = filedialog.askopenfilename(title="Select MouseInfo Log", filetypes=[("Text files", "*.txt")])

    if file_path and os.path.exists(file_path):
        movements.clear()
        try:
            with open(file_path, 'r') as file:
                # Print the content of the file for debugging
                print(f"Opening file: {file_path}")
                file_content = file.readlines()
                print("File content:")
                for line in file_content:
                    print(line.strip())

                # Process the file content
                for line in file_content:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        try:
                            x, y = int(parts[0].strip()), int(parts[1].strip())
                            event_type = None
                            movements.append([x, y, event_type])
                        except ValueError:
                            status_label.config(text="Error: Invalid coordinates in file.")
                            return

            # Debugging: Print movements list
            print("Movements loaded:")
            for move in movements:
                print(move)

            status_label.config(text="Log loaded successfully. Please mark clicks.")
            mark_clicks()  # Prompt user to add clicks
        except Exception as e:
            status_label.config(text=f"Error loading log file: {e}")
    else:
        status_label.config(text="Failed to load log file.")


# Function to mark click events
def mark_clicks():
    def add_click(event_type):
        selected_index = click_listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            movements[idx][2] = event_type
            click_listbox.delete(idx)
            click_listbox.insert(idx, f"{movements[idx][0]}, {movements[idx][1]} - {event_type.capitalize()} Click")
            status_label.config(text=f"{event_type.capitalize()} click set at position {idx + 1}")

    # New window for marking clicks
    click_window = tk.Toplevel(root)
    click_window.title("Mark Click Events")

    # Listbox showing all movement coordinates
    click_listbox = tk.Listbox(click_window, width=50)
    click_listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Clear previous items if any
    click_listbox.delete(0, tk.END)

    # Debugging: Print movements to verify correct data
    print("Movements to display:")
    for i, move in enumerate(movements):
        print(f"{move[0]}, {move[1]} - No Click")  # Debug output
        click_listbox.insert(i, f"{move[0]}, {move[1]} - No Click")

    # Buttons to mark clicks
    left_click_btn = ttkb.Button(click_window, text="Mark Left Click", command=lambda: add_click('left'))
    left_click_btn.grid(row=1, column=0, padx=5, pady=5)

    right_click_btn = ttkb.Button(click_window, text="Mark Right Click", command=lambda: add_click('right'))
    right_click_btn.grid(row=1, column=1, padx=5, pady=5)

    # Save and close the window after marking clicks
    def close_click_window():
        click_window.destroy()
        status_label.config(text="Clicks marked. Ready for replay.")

    close_btn = ttkb.Button(click_window, text="Save and Close", command=close_click_window)
    close_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)


# Function to cancel replay
def cancel_replay_fn():
    global cancel_replay
    cancel_replay = True


# Function to replay the loaded movements
def replay_movements():
    global movements
    global cancel_replay
    if not movements:
        status_label.config(text="No movements loaded.")
        return
    try:
        delay = float(delay_entry.get())
        repeat_count = int(repeat_entry.get())
        if delay < 0:
            status_label.config(text="Delay cannot be negative.")
            return
        if not movements:
            status_label.config(text="No movements recorded or loaded.")
            return

        # Disable buttons while replaying
        start_btn.config(state=tk.DISABLED)
        load_log_btn.config(state=tk.DISABLED)
        replay_btn.config(state=tk.DISABLED)
        cancel_btn.config(state=tk.NORMAL)

        cancel_replay = False
        status_label.config(text="Replaying movements...")

        # Replaying in a new thread to avoid blocking the GUI
        def replay_thread():
            for _ in range(repeat_count):
                for movement in movements:
                    if cancel_replay:
                        status_label.config(text="Replay cancelled.")
                        return
                    x, y, event_type = movement  # Unpack x, y, and event_type
                    pyautogui.moveTo(x, y)  # Move to recorded position
                    if event_type == 'left':
                        pyautogui.click(button='left')  # Simulate left click
                        time.sleep(delay)  # Only apply delay before clicks
                    elif event_type == 'right':
                        pyautogui.click(button='right')  # Simulate right click
                        time.sleep(delay)
            status_label.config(text="Replay finished.")

            # Re-enable buttons after replay
            start_btn.config(state=tk.NORMAL)
            load_log_btn.config(state=tk.NORMAL)
            replay_btn.config(state=tk.NORMAL)
            cancel_btn.config(state=tk.DISABLED)

            # Focus on the program window after replay finishes
            # focus_on_window()

        threading.Thread(target=replay_thread).start()

    except ValueError:
        status_label.config(text="Invalid delay/repeat value. Please enter a valid number.")


# Function to start listening for the ESC key to close the program
def esc_hotkey_listener():
    keyboard.add_hotkey('esc', root.quit)


# GUI Setup
root = tk.Tk()
root.title("Mouse Recorder with MouseInfo")

# Initialize ttkbootstrap style
style = ttkb.Style()
style.theme_use('darkly')  # Example theme

# Define custom style for buttons
style.configure('Custom.TButton',
                background='#3498db',  # Button color
                foreground='white',
                borderwidth=2,
                relief='flat')

style.map('Custom.TButton',
          background=[('active', '#2980b9')],  # Color when hovered
          foreground=[('active', 'white')],
          state=[('disabled', '#d3d3d3')])  # Grey color when disabled

# Define custom style for cancel button
style.configure('Cancel.TButton',
                background='red',
                foreground='white',
                borderwidth=2,
                relief='flat')

style.map('Cancel.TButton',
          background=[('active', '#ff4d4d')],  # Color when hovered
          foreground=[('active', 'white')],
          state=[('disabled', '#d3d3d3')])  # Grey color when disabled


# Delay Input
delay_label = ttkb.Label(root, text="Set Delay (seconds) before Clicks:")
delay_label.grid(row=0, column=0, padx=10, pady=10)

delay_entry = ttkb.Entry(root)
delay_entry.grid(row=0, column=1, padx=10, pady=10)

# Repeat Entry
repeat_label = ttk.Label(root, text="Repeat Count:")
repeat_label.grid(row=1, column=0, padx=10, pady=10)

repeat_entry = ttk.Entry(root)
repeat_entry.grid(row=1, column=1, padx=10, pady=10)

# Start Recording (opens MouseInfo)
start_btn = ttkb.Button(root, text="Start Recording (MouseInfo)", command=start_mouseinfo, style='Custom.TButton')
start_btn.grid(row=2, column=0, padx=10, pady=10)

# Load Log Button
load_log_btn = ttkb.Button(root, text="Load Log", command=load_log, style='Custom.TButton')
load_log_btn.grid(row=2, column=1, padx=10, pady=10)

# Replay Button
replay_btn = ttkb.Button(root, text="Replay Movements", command=replay_movements, style='Custom.TButton')
replay_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Cancel Replay Button
cancel_btn = ttkb.Button(root, text="Cancel Replay", command=cancel_replay_fn, style='Cancel.TButton')
cancel_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
cancel_btn.config(state=tk.DISABLED)  # Initially disabled

# Status Label
status_label = ttkb.Label(root, text="")
status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Start ESC hotkey listener
esc_hotkey_listener()

root.mainloop()
