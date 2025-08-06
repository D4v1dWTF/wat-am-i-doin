import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from pypresence import Presence
import threading
import time

class DiscordStatusEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("wat am i doin v1.0")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        # Set window icon and style
        self.root.configure(bg='#1a1a1a')
        
        # Discord RPC setup
        self.rpc = None
        self.is_connected = False
        self.current_activity = ""
        
        # Load saved activities
        self.saved_activities = self.load_saved_activities()
        
        self.setup_ui()
        self.connect_discord()
    
    def setup_ui(self):
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Cyber.TFrame', background='#1a1a1a')
        style.configure('Cyber.TLabel', background='#1a1a1a', foreground='#00ff88', font=('Segoe UI', 10))
        style.configure('Title.TLabel', background='#1a1a1a', foreground='#00ff88', font=('Segoe UI', 18, 'bold'))
        style.configure('Status.TLabel', background='#1a1a1a', foreground='#ffaa00', font=('Segoe UI', 9))
        style.configure('Cyber.TButton', background='#2d2d2d', foreground='#00ff88', font=('Segoe UI', 9))
        style.map('Cyber.TButton', background=[('active', '#3d3d3d')])
        
        # Main frame with cyberpunk styling
        main_frame = ttk.Frame(self.root, padding="25", style='Cyber.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title with glow effect
        title_label = ttk.Label(main_frame, text="WAT AM I DOIN", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Customize your Discord presence", style='Cyber.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Connection status with cyberpunk styling
        self.status_label = ttk.Label(main_frame, text="Status: Connecting...", style='Status.TLabel')
        self.status_label.grid(row=2, column=0, columnspan=2, pady=(0, 25))
        
        # Activity input section
        input_frame = ttk.Frame(main_frame, style='Cyber.TFrame')
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(input_frame, text="Enter your activity:", style='Cyber.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # Custom styled entry
        self.activity_entry = tk.Entry(input_frame, width=45, font=('Segoe UI', 10), 
                                     bg='#2d2d2d', fg='#00ff88', insertbackground='#00ff88',
                                     relief='flat', bd=0)
        self.activity_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.activity_entry.bind('<Return>', self.update_activity)
        
        # Buttons frame with cyberpunk styling
        btn_frame = ttk.Frame(main_frame, style='Cyber.TFrame')
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0, 25))
        
        # Update button
        update_btn = tk.Button(btn_frame, text="UPDATE ACTIVITY", command=self.update_activity,
                              bg='#00ff88', fg='#1a1a1a', font=('Segoe UI', 9, 'bold'),
                              relief='flat', bd=0, padx=15, pady=8)
        update_btn.grid(row=0, column=0, padx=(0, 8))
        
        # Save Status button
        save_btn = tk.Button(btn_frame, text="SAVE STATUS", command=self.save_status_with_name,
                            bg='#2d2d2d', fg='#00ff88', font=('Segoe UI', 9, 'bold'),
                            relief='flat', bd=0, padx=15, pady=8)
        save_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Clear activity button
        clear_btn = tk.Button(btn_frame, text="CLEAR ACTIVITY", command=self.clear_activity,
                             bg='#2d2d2d', fg='#ff6b6b', font=('Segoe UI', 9, 'bold'),
                             relief='flat', bd=0, padx=15, pady=8)
        clear_btn.grid(row=0, column=2)
        
        # Saved activities section
        saved_frame = ttk.Frame(main_frame, style='Cyber.TFrame')
        saved_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(saved_frame, text="SAVED STATUSES:", style='Cyber.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        # Listbox with cyberpunk styling
        self.saved_listbox = tk.Listbox(saved_frame, height=8, width=50, 
                                       bg='#2d2d2d', fg='#00ff88', 
                                       selectbackground='#00ff88', selectforeground='#1a1a1a',
                                       font=('Segoe UI', 9), relief='flat', bd=0)
        self.saved_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(saved_frame, orient=tk.VERTICAL, command=self.saved_listbox.yview,
                                bg='#2d2d2d', troughcolor='#1a1a1a', width=12)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.saved_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Bottom buttons with cyberpunk styling
        btn_frame2 = ttk.Frame(main_frame, style='Cyber.TFrame')
        btn_frame2.grid(row=6, column=0, columnspan=2, pady=(15, 0))
        
        use_btn = tk.Button(btn_frame2, text="USE SELECTED", command=self.use_saved_activity,
                           bg='#2d2d2d', fg='#00ff88', font=('Segoe UI', 8, 'bold'),
                           relief='flat', bd=0, padx=12, pady=6)
        use_btn.grid(row=0, column=0, padx=(0, 8))
        
        delete_btn = tk.Button(btn_frame2, text="DELETE SELECTED", command=self.delete_saved_activity,
                              bg='#2d2d2d', fg='#ff6b6b', font=('Segoe UI', 8, 'bold'),
                              relief='flat', bd=0, padx=12, pady=6)
        delete_btn.grid(row=0, column=1, padx=(0, 8))
        
        clear_all_btn = tk.Button(btn_frame2, text="CLEAR ALL", command=self.clear_all_saved,
                                 bg='#2d2d2d', fg='#ff6b6b', font=('Segoe UI', 8, 'bold'),
                                 relief='flat', bd=0, padx=12, pady=6)
        clear_all_btn.grid(row=0, column=2)
        
        # Load saved activities into listbox
        self.refresh_saved_activities()
        
        # Bind double-click to use saved activity
        self.saved_listbox.bind('<Double-Button-1>', self.use_saved_activity)
        
        # Add hover effects
        self.add_hover_effects(update_btn, save_btn, clear_btn, use_btn, delete_btn, clear_all_btn)
    
    def add_hover_effects(self, *buttons):
        """Add hover effects to buttons"""
        for btn in buttons:
            btn.bind('<Enter>', lambda e, b=btn: self.on_button_hover(b, True))
            btn.bind('<Leave>', lambda e, b=btn: self.on_button_hover(b, False))
    
    def on_button_hover(self, button, entering):
        """Handle button hover effects"""
        if entering:
            if button.cget('bg') == '#00ff88':
                button.configure(bg='#00cc6a')
            elif button.cget('bg') == '#2d2d2d':
                button.configure(bg='#3d3d3d')
        else:
            if button.cget('bg') == '#00cc6a':
                button.configure(bg='#00ff88')
            elif button.cget('bg') == '#3d3d3d':
                button.configure(bg='#2d2d2d')
    
    def connect_discord(self):
        """Connect to Discord RPC"""
        try:
            # Load client ID from file or ask user
            client_id = self.load_client_id()
            if not client_id:
                return
            
            self.rpc = Presence(client_id)
            self.rpc.connect()
            self.is_connected = True
            self.status_label.config(text="Status: Connected to Discord", foreground='#00ff88')
        except Exception as e:
            self.is_connected = False
            self.status_label.config(text="Status: Failed to connect", foreground='#ff6b6b')
            messagebox.showerror("Connection Error", f"Failed to connect to Discord: {str(e)}\n\nPlease make sure:\n1. Discord is running\n2. You have set the correct client ID")
    
    def load_client_id(self):
        """Load client ID from file or ask user"""
        if os.path.exists("discord_app_id.txt"):
            with open("discord_app_id.txt", "r") as f:
                return f.read().strip()
        else:
            # Ask user for client ID with simplified instructions
            client_id = simpledialog.askstring("Discord App Setup", 
                "🔧 Quick Setup Required!\n\n1. Go to: https://discord.com/developers/applications\n2. Click 'New Application'\n3. Name it anything (e.g., 'My Status')\n4. Copy the 'Application ID' number\n5. Paste it here:")
            
            if client_id:
                with open("discord_app_id.txt", "w") as f:
                    f.write(client_id)
                return client_id
            else:
                messagebox.showerror("Error", "App ID is required to connect to Discord!")
                return None
    
    def update_activity(self, event=None):
        """Update Discord activity"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to Discord!")
            return
        
        activity = self.activity_entry.get().strip()
        if not activity:
            messagebox.showerror("Error", "Please enter an activity!")
            return
        
        try:
            self.rpc.update(
                state=activity,
                details="Custom Activity",
                large_image="default",
                large_text="wat am i doin"
            )
            self.current_activity = activity
            messagebox.showinfo("Success", f"✅ Status updated to: {activity}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update activity: {str(e)}")
    
    def clear_activity(self):
        """Clear Discord activity"""
        if not self.is_connected:
            messagebox.showerror("Error", "Not connected to Discord!")
            return
        
        try:
            self.rpc.clear()
            self.current_activity = ""
            self.activity_entry.delete(0, tk.END)
            messagebox.showinfo("Success", "✅ Status cleared!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear activity: {str(e)}")
    
    def save_status_with_name(self):
        """Save current status with a custom name"""
        activity = self.activity_entry.get().strip()
        if not activity:
            messagebox.showerror("Error", "Please enter an activity to save!")
            return
        
        # Ask for a name for this status
        status_name = simpledialog.askstring("Save Status", "Enter a name for this status:")
        if not status_name:
            return
        
        # Check if name already exists
        existing_names = [item.split(": ")[0] for item in self.saved_activities]
        if status_name in existing_names:
            if not messagebox.askyesno("Confirm", f"Status '{status_name}' already exists. Overwrite it?"):
                return
            # Remove existing entry
            self.saved_activities = [item for item in self.saved_activities if not item.startswith(status_name + ": ")]
        
        # Add new status
        status_entry = f"{status_name}: {activity}"
        self.saved_activities.append(status_entry)
        self.save_saved_activities()
        self.refresh_saved_activities()
        messagebox.showinfo("Success", f"✅ Status '{status_name}' saved!")
    
    def use_saved_activity(self, event=None):
        """Use selected saved activity"""
        selection = self.saved_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a status!")
            return
        
        status_entry = self.saved_activities[selection[0]]
        # Extract the activity part (after the colon)
        activity = status_entry.split(": ", 1)[1]
        self.activity_entry.delete(0, tk.END)
        self.activity_entry.insert(0, activity)
        self.update_activity()
    
    def delete_saved_activity(self):
        """Delete selected saved activity"""
        selection = self.saved_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a status to delete!")
            return
        
        status_entry = self.saved_activities[selection[0]]
        status_name = status_entry.split(": ")[0]
        if messagebox.askyesno("Confirm", f"Delete status '{status_name}'?"):
            self.saved_activities.pop(selection[0])
            self.save_saved_activities()
            self.refresh_saved_activities()
    
    def clear_all_saved(self):
        """Clear all saved activities"""
        if not self.saved_activities:
            messagebox.showinfo("Info", "No saved statuses to clear!")
            return
        
        if messagebox.askyesno("Confirm", f"Delete all {len(self.saved_activities)} saved statuses?"):
            self.saved_activities.clear()
            self.save_saved_activities()
            self.refresh_saved_activities()
            messagebox.showinfo("Success", "✅ All saved statuses cleared!")
    
    def refresh_saved_activities(self):
        """Refresh the saved activities listbox"""
        self.saved_listbox.delete(0, tk.END)
        for activity in self.saved_activities:
            self.saved_listbox.insert(tk.END, activity)
    
    def load_saved_activities(self):
        """Load saved activities from file"""
        try:
            if os.path.exists("saved_statuses.json"):
                with open("saved_statuses.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_saved_activities(self):
        """Save activities to file"""
        try:
            with open("saved_statuses.json", "w") as f:
                json.dump(self.saved_activities, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save activities: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_connected and self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except:
                pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = DiscordStatusEditor(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 