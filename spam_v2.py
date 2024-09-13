import tkinter as tk
from tkinter import ttk
import subprocess
import time
import threading
import os
import pyautogui
import keyboard
from tkinter import filedialog, messagebox
import ttkbootstrap as ttkb

# List to store parsed mouse movements and clicks
movements = []

# Global variable to control replay cancellation
cancel_replay = False


# ------------------- MouseInfo and Log Functions -------------------

def start_mouseinfo():
    """Start MouseInfo via command line."""
    status_label.config(text="MouseInfo opened. Record movements using F6 and save the log")
    subprocess.Popen(['py', '-m', 'mouseinfo'])


def load_log():
    """Load mouse movements from a text file."""
    global movements
    file_path = filedialog.askopenfilename(title="Select MouseInfo Log", filetypes=[("Text files", "*.txt")])

    if file_path and os.path.exists(file_path):
        movements.clear()
        try:
            with open(file_path, 'r') as file:
                file_content = file.readlines()

                # Process the file content
                for line in file_content:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        try:
                            x, y = int(parts[0].strip()), int(parts[1].strip())
                            event_type = parts[2].strip() if len(parts) > 2 else None
                            movements.append([x, y, event_type])
                        except ValueError:
                            status_label.config(text="Error: Invalid coordinates in file.", foreground="red")
                            return

            status_label.config(text="Log loaded successfully. Please mark clicks.", foreground="green")
            # Prompt user to add clicks
            mark_clicks()
        except Exception as e:
            status_label.config(text=f"Error loading log file: {e}", foreground="red")
    else:
        status_label.config(text="Failed to load log file.", foreground="red")


def export_log():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")],
                                             title="Save Coordinates Log")

    if file_path:
        try:
            with open(file_path, 'w') as file:
                for move in movements:
                    x, y, event_type = move
                    file.write(f"{x},{y},{event_type if event_type else ''}\n")
            status_label.config(text="Log exported successfully.", foreground="green")
        except Exception as e:
            status_label.config(text=f"Error exporting log: {e}", foreground="red")


# ------------------- Click Marking and Replay Functions -------------------

def mark_clicks():
    """Mark click events in the loaded mouse movements."""

    def add_click(event_type):
        """Add a click event (left/right) to the selected movement."""
        selected_index = click_listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            movements[idx][2] = event_type
            click_listbox.delete(idx)
            click_listbox.insert(idx, f"{movements[idx][0]}, {movements[idx][1]}, {event_type.capitalize()} Click")
            mark_status_label.config(text=f"{event_type.capitalize()} click set at position {idx + 1}")

    def remove_click():
        """Remove a click event from the selected movement."""
        selected_index = click_listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            movements[idx][2] = None
            click_listbox.delete(idx)
            click_listbox.insert(idx, f"{movements[idx][0]}, {movements[idx][1]}, No Click")
            mark_status_label.config(text=f"Click removed at position {idx + 1}")

    def delete_item():
        """Remove a movement event from the list."""
        selected_index = click_listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            click_listbox.delete(idx)
            movements.pop(idx)
            mark_status_label.config(text=f"Item at position {idx + 1} deleted.")

    def move_cursor(x, y):
        """Move cursor."""
        pyautogui.moveTo(x, y)
        mark_status_label.config(text=f"Moved mouse to {x}, {y}")

    def move_cursor_to():
        """Move cursor to the selected coordinates."""
        selected_index = click_listbox.curselection()
        if selected_index:
            idx = selected_index[0]
            x, y = movements[idx][0], movements[idx][1]
            move_cursor(x, y)

    def show_context_menu(event):
        """Show context menu."""
        try:
            click_listbox.selection_clear(0, tk.END)
            click_listbox.selection_set(click_listbox.nearest(event.y))
            context_menu.post(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    # New window for marking clicks
    click_window = tk.Toplevel(root)
    click_window.title("Mark Click Events")

    # Listbox to display movements
    click_listbox = tk.Listbox(click_window, width=50)
    click_listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    # Clear previous items if any
    click_listbox.delete(0, tk.END)

    # List all movements inside listbox
    for i, move in enumerate(movements):
        click_listbox.insert(i, f"{move[0]}, {move[1]}, {move[2] if move[2] else 'No'} Click")

    # Right-click event
    click_listbox.bind("<Button-3>", show_context_menu)

    # Create context menu
    context_menu = tk.Menu(click_window, tearoff=0)
    context_menu.add_command(label="Add Left Click", command=lambda: add_click('left'))
    context_menu.add_command(label="Add Right Click", command=lambda: add_click('right'))
    context_menu.add_command(label="Remove Click", command=remove_click)
    context_menu.add_separator()
    context_menu.add_command(label="Move Cursor To", command=move_cursor_to)
    context_menu.add_separator()
    context_menu.add_command(label="Delete Item", command=delete_item)

    # Export Button
    export_btn = ttkb.Button(click_window, text="Export Log", command=export_log)
    export_btn.grid(row=4, column=1, padx=10, pady=10, sticky='se')

    # Status Label for information
    mark_status_label = ttkb.Label(click_window, text="")
    mark_status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Save and close the window after marking clicks
    def close_click_window():
        click_window.destroy()
        status_label.config(text="Clicks marked. Ready for replay.", foreground="white")

    close_btn = ttkb.Button(click_window, text="Save and Close", command=close_click_window)
    close_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)


def replay_movements():
    """Replay the recorded movements with a delay."""
    global cancel_replay
    try:
        delay = float(delay_entry.get())
        repeat_count = int(repeat_entry.get())
        if delay < 0:
            status_label.config(text="Delay cannot be negative.", foreground="red")
            return
        if repeat_count <= 0:
            status_label.config(text="Repeat count cannot be negative.", foreground="red")
            return
        if not movements:
            status_label.config(text="No movements recorded or loaded.", foreground="red")
            return

        toggle_buttons(state=tk.DISABLED)

        cancel_replay = False
        status_label.config(text="Replaying movements...", foreground="white")

        # Start replay in a separate thread to avoid blocking the GUI
        def replay_thread():
            for _ in range(repeat_count):
                for movement in movements:
                    if cancel_replay:
                        status_label.config(text="Replay cancelled.", foreground="white")
                        return
                    x, y, event_type = movement  # Unpack x, y, and event_type
                    pyautogui.moveTo(x, y)  # Move to recorded position
                    if event_type == 'left':
                        pyautogui.click(button='left')  # Simulate left click
                        time.sleep(delay)  # Only apply delay before clicks
                    elif event_type == 'right':
                        pyautogui.click(button='right')  # Simulate right click
                        time.sleep(delay)
            status_label.config(text="Replay finished.", foreground="green")
            reset_buttons()

        threading.Thread(target=replay_thread).start()
    except ValueError:
        status_label.config(text="Invalid input.", foreground="red")


# ------------------- Utility Functions -------------------

def cancel_replay_fn():
    """Cancel the current replay and re-enable buttons."""
    global cancel_replay
    cancel_replay = True
    status_label.config(text="Replay cancelled.", foreground="white")
    reset_buttons()


def reset_buttons():
    """Re-enable buttons after replay or cancellation."""
    start_btn.config(state=tk.NORMAL)
    load_log_btn.config(state=tk.NORMAL)
    replay_btn.config(state=tk.NORMAL)
    cancel_btn.config(state=tk.DISABLED)


def toggle_buttons(state):
    """Toggle the state of buttons during replay."""
    start_btn.config(state=state)
    load_log_btn.config(state=state)
    replay_btn.config(state=state)
    cancel_btn.config(state=tk.NORMAL if state == tk.DISABLED else state)


# ------------------- ESC Hotkey Listener -------------------

def esc_hotkey_listener():
    """Listen for 'Esc' key press to cancel the replay."""
    keyboard.add_hotkey('esc', cancel_replay_fn)


# ------------------- GUI Setup -------------------

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
          state=[('disabled', '#d3d3d3')])  # Grey color when disabled

# Define custom style for start button
style.configure('Start.TButton',
                background='green',  # Button color
                foreground='white',
                borderwidth=2,
                relief='flat')

style.map('Custom.TButton',
          state=[('disabled', '#d3d3d3')])  # Grey color when disabled

# Define custom style for cancel button
style.configure('Cancel.TButton',
                background='red',
                foreground='white',
                borderwidth=2,
                relief='flat')

style.map('Cancel.TButton',
          state=[('disabled', '#d3d3d3')])  # Grey color when disabled

# Delay Input
delay_label = ttkb.Label(root, text="Delay in seconds before Clicks:")
delay_label.grid(row=0, column=0, padx=10, pady=10)

delay_entry = ttkb.Entry(root)
delay_entry.grid(row=0, column=1, padx=10, pady=10)

# Repeat Entry
repeat_label = ttk.Label(root, text="Repeat Counter:")
repeat_label.grid(row=1, column=0, padx=10, pady=10)

repeat_entry = ttk.Entry(root)
repeat_entry.grid(row=1, column=1, padx=10, pady=10)

# Start Recording (opens MouseInfo)
start_btn = ttkb.Button(root, text="Record Movements (MouseInfo)", command=start_mouseinfo, style='Custom.TButton')
start_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Load Log Button
load_log_btn = ttkb.Button(root, text="Load Coordinates", command=load_log, style='Custom.TButton')
load_log_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Replay Button
replay_btn = ttkb.Button(root, text="Start Replay", command=replay_movements, style='Start.TButton')
replay_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Cancel Replay Button
cancel_btn = ttkb.Button(root, text="Cancel Replay", command=cancel_replay_fn, style='Cancel.TButton')
cancel_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
cancel_btn.config(state=tk.DISABLED)  # Initially disabled

# Status Label
status_label = ttkb.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

# Start the Esc listener
esc_hotkey_listener()

root.mainloop()
