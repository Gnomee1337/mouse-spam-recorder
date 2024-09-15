import tkinter as tk
from tkinter import ttk, filedialog
import ttkbootstrap as ttkb
import time
import os
import threading
import pyautogui
import keyboard
import mouseinfo
import multiprocessing


class MouseRecorderApp:
    def __init__(self, root):
        # List to store parsed mouse movements and clicks
        self.movements = []

        # Variable to control replay cancellation
        self.cancel_replay = False

        # ------------------- GUI Setup -------------------
        self.root = root
        self.root.title("Mouse Recorder with MouseInfo")

        # Initialize ttkbootstrap style
        self.style = ttkb.Style()
        self.style.theme_use('darkly')  # Example theme
        # Create and configure style for buttons
        self.configure_style()

        # Delay Input
        self.delay_label = ttkb.Label(root, text="Delay in seconds before Clicks:")
        self.delay_label.grid(row=0, column=0, padx=10, pady=10)

        self.delay_entry = ttkb.Entry(root)
        self.delay_entry.grid(row=0, column=1, padx=10, pady=10)

        # Repeat Entry
        self.repeat_label = ttk.Label(root, text="Repeat Counter:")
        self.repeat_label.grid(row=1, column=0, padx=10, pady=10)

        self.repeat_entry = ttk.Entry(root)
        self.repeat_entry.grid(row=1, column=1, padx=10, pady=10)

        # Start Recording (opens MouseInfo)
        self.start_btn = ttk.Button(root, text="Record Movements (MouseInfo)", command=self.start_mouseinfo,
                                    style='Custom.TButton')
        self.start_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Load Log Button
        self.load_log_btn = ttkb.Button(root, text="Load Coordinates", command=self.load_log, style='Custom.TButton')
        self.load_log_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Replay Button
        self.replay_btn = ttkb.Button(root, text="Start Replay", command=self.replay_movements, style='Start.TButton')
        self.replay_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Cancel Replay Button
        self.cancel_btn = ttkb.Button(root, text="Cancel Replay", command=self.cancel_replay_fn, style='Cancel.TButton')
        self.cancel_btn.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
        self.cancel_btn.config(state=tk.DISABLED)  # Initially disabled

        # Status Label
        self.status_label = ttkb.Label(root, text="")
        self.status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Start the Esc listener
        self.esc_hotkey_listener()

    def configure_style(self):
        """Configure custom style for buttons."""
        # Define custom style for buttons
        self.style.configure('Custom.TButton',
                             background='#3498db',  # Button color
                             foreground='white',
                             borderwidth=2,
                             relief='flat')
        self.style.map('Custom.TButton',
                       state=[('disabled', '#d3d3d3')])  # Grey color when disabled

        # Define custom style for START button
        self.style.configure('Start.TButton',
                             background='green',  # Button color
                             foreground='white',
                             borderwidth=2,
                             relief='flat')
        self.style.map('Custom.TButton',
                       state=[('disabled', '#d3d3d3')])  # Grey color when disabled

        # Define custom style for CANCEL button
        self.style.configure('Cancel.TButton',
                             background='red',
                             foreground='white',
                             borderwidth=2,
                             relief='flat')
        self.style.map('Cancel.TButton',
                       state=[('disabled', '#d3d3d3')])  # Grey color when disabled

    # ------------------- MouseInfo and Log Functions -------------------

    def start_mouseinfo(self):
        """Start the MouseInfo GUI in a separate process"""
        process = multiprocessing.Process(target=run_mouseinfo)
        process.start()

    def load_log(self):
        """Load mouse movements from a text file."""
        file_path = filedialog.askopenfilename(title="Select MouseInfo Log", filetypes=[("Text files", "*.txt")])

        if file_path and os.path.exists(file_path):
            self.movements.clear()
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
                                self.movements.append([x, y, event_type])
                            except ValueError:
                                self.status_label.config(text="Error: Invalid coordinates in file.", foreground="red")
                                return

                self.status_label.config(text="Log loaded successfully. Please mark clicks.", foreground="green")
                # Prompt user to add clicks
                self.mark_clicks()
            except Exception as e:
                self.status_label.config(text=f"Error loading log file: {e}", foreground="red")
        else:
            self.status_label.config(text="Failed to load log file.", foreground="red")

    def export_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")],
                                                 title="Save Coordinates Log")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    for move in self.movements:
                        x, y, event_type = move
                        file.write(f"{x},{y},{event_type if event_type else ''}\n")
                self.status_label.config(text="Log exported successfully.", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"Error exporting log: {e}", foreground="red")

    # ------------------- Click Marking and Replay Functions -------------------

    def mark_clicks(self):
        """Mark click events in the loaded mouse movements."""

        def add_click(event_type):
            """Add a click event (left/right) to the selected movement."""
            selected_index = click_listbox.curselection()
            if selected_index:
                idx = selected_index[0]
                self.movements[idx][2] = event_type
                click_listbox.delete(idx)
                click_listbox.insert(idx,
                                     f"{self.movements[idx][0]}, {self.movements[idx][1]}, {event_type.capitalize()} Click")
                mark_status_label.config(text=f"{event_type.capitalize()} click set at position {idx + 1}")

        def remove_click():
            """Remove a click event from the selected movement."""
            selected_index = click_listbox.curselection()
            if selected_index:
                idx = selected_index[0]
                self.movements[idx][2] = None
                click_listbox.delete(idx)
                click_listbox.insert(idx, f"{self.movements[idx][0]}, {self.movements[idx][1]}, No Click")
                mark_status_label.config(text=f"Click removed at position {idx + 1}")

        def delete_item():
            """Remove a movement event from the list."""
            selected_index = click_listbox.curselection()
            if selected_index:
                idx = selected_index[0]
                click_listbox.delete(idx)
                self.movements.pop(idx)
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
                x, y = self.movements[idx][0], self.movements[idx][1]
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
        click_window = tk.Toplevel(self.root)
        click_window.title("Mark Click Events")

        # Listbox to display movements
        click_listbox = tk.Listbox(click_window, width=50)
        click_listbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Clear previous items if any
        click_listbox.delete(0, tk.END)

        # List all movements inside listbox
        for i, move in enumerate(self.movements):
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
        export_btn = ttkb.Button(click_window, text="Export Log", command=self.export_log)
        export_btn.grid(row=4, column=1, padx=10, pady=10, sticky='se')

        # Status Label for information
        mark_status_label = ttkb.Label(click_window, text="")
        mark_status_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Save and close the window after marking clicks
        def close_click_window():
            click_window.destroy()
            self.status_label.config(text="Clicks marked. Ready for replay.", foreground="white")

        close_btn = ttkb.Button(click_window, text="Save and Close", command=close_click_window)
        close_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

    def replay_movements(self):
        """Replay the recorded movements with a delay."""
        try:
            delay = float(self.delay_entry.get())
            repeat_count = int(self.repeat_entry.get())
            if delay < 0:
                self.status_label.config(text="Delay cannot be negative.", foreground="red")
                return
            if repeat_count <= 0:
                self.status_label.config(text="Repeat count cannot be negative.", foreground="red")
                return
            if not self.movements:
                self.status_label.config(text="No movements recorded or loaded.", foreground="red")
                return

            self.toggle_buttons(state=tk.DISABLED)

            self.cancel_replay = False
            self.status_label.config(text="Replaying movements...", foreground="white")

            # Start replay in a separate thread to avoid blocking the GUI
            def replay_thread():
                for _ in range(repeat_count):
                    for movement in self.movements:
                        if self.cancel_replay:
                            self.status_label.config(text="Replay cancelled.", foreground="white")
                            return
                        x, y, event_type = movement  # Unpack x, y, and event_type
                        pyautogui.moveTo(x, y)  # Move to recorded position
                        if event_type == 'left':
                            pyautogui.click(button='left')  # Simulate left click
                            time.sleep(delay)  # Only apply delay before clicks
                        elif event_type == 'right':
                            pyautogui.click(button='right')  # Simulate right click
                            time.sleep(delay)
                self.status_label.config(text="Replay finished.", foreground="green")
                self.reset_buttons()

            threading.Thread(target=replay_thread).start()
        except ValueError:
            self.status_label.config(text="Invalid input.", foreground="red")

    # ------------------- Utility Functions -------------------

    def cancel_replay_fn(self):
        """Cancel the current replay and re-enable buttons."""
        self.cancel_replay = True
        self.status_label.config(text="Replay cancelled.", foreground="white")
        self.reset_buttons()

    def reset_buttons(self):
        """Re-enable buttons after replay or cancellation."""
        self.start_btn.config(state=tk.NORMAL)
        self.load_log_btn.config(state=tk.NORMAL)
        self.replay_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)

    def toggle_buttons(self, state):
        """Toggle the state of buttons during replay."""
        self.start_btn.config(state=state)
        self.load_log_btn.config(state=state)
        self.replay_btn.config(state=state)
        self.cancel_btn.config(state=tk.NORMAL if state == tk.DISABLED else state)

    # ------------------- ESC Hotkey Listener -------------------

    def esc_hotkey_listener(self):
        """Listen for 'Esc' key press to cancel the replay."""
        keyboard.add_hotkey('esc', self.cancel_replay_fn)


def run_mouseinfo():
    """Function to launch MouseInfo in a separate process"""
    try:
        mouseinfo.MouseInfoWindow()  # Launch the MouseInfo GUI
    except Exception as e:
        print(f"Error starting MouseInfo GUI: {e}")


if __name__ == "__main__":
    """This ensures the multiprocessing works when creating an executable"""
    # Main program setup
    multiprocessing.freeze_support()  # Required for PyInstaller compatibility

    root = tk.Tk()
    app = MouseRecorderApp(root)  # Create an instance of the application class
    root.mainloop()
