import os
import sys
import json
import zipfile
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox

# Base URL for the hosted extension packages
# These are served from the downloads/packages/ directory on the website
BASE_URL = "https://sporlyworks.com/downloads/packages"
MAP_URL = f"{BASE_URL}/category_map.json"

# Fallback: try loading category_map.json from the same directory as the executable
def get_local_map_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'category_map.json')
    return os.path.join(os.path.dirname(__file__), '..', 'category_map.json')

# Set up local suite directory based on OS
HOME_DIR = os.path.expanduser("~")
SUITE_DIR = os.path.join(HOME_DIR, "SporlyWorks_Suite")

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SporlyWorks Native Installer")
        self.root.geometry("800x600")
        self.root.configure(bg="#1E1E1E")
        
        self.categories = {}
        self.check_vars = {}
        self.all_extensions = {}
        
        self._setup_ui()
        self._load_data()
        
    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1E1E1E")
        style.configure("TLabel", background="#1E1E1E", foreground="#FFFFFF", font=("Inter", 11))
        style.configure("Header.TLabel", font=("Inter", 16, "bold"), padding=(0, 10))
        style.configure("TButton", font=("Inter", 11, "bold"), background="#8B5CF6", foreground="white")
        style.configure("TCheckbutton", background="#1E1E1E", foreground="#CCCCCC", font=("Inter", 10))
        
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(top_frame, text="SporlyWorks Complete Suite Installer", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Install Selected", command=self.install_selected).pack(side=tk.RIGHT)
        
        # Notebook for categories
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
        
    def _load_data(self):
        data = None
        # Try remote first
        try:
            req = urllib.request.Request(MAP_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
        except Exception:
            pass
        
        # Fallback to local file
        if data is None:
            local_path = get_local_map_path()
            if os.path.isfile(local_path):
                with open(local_path, 'r') as f:
                    data = json.load(f)
        
        if data is None:
            messagebox.showerror("Connection Error", 
                "Failed to fetch extension list.\n\n"
                "Please check your internet connection and try again.")
            return
        
        self.all_extensions = data
        for ext_id, ext_info in data.items():
            cat = ext_info.get("cws", "Other")
            if cat not in self.categories:
                self.categories[cat] = []
            self.categories[cat].append((ext_id, ext_info["title"]))
        
        self._populate_notebook()

    def _populate_notebook(self):
        for category, extensions in self.categories.items():
            frame = ttk.Frame(self.notebook)
            
            # Simple canvas + scrollbar for many items
            canvas = tk.Canvas(frame, bg="#1E1E1E", highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")
            
            ttk.Label(scrollable_frame, text=f"{category} Extensions", style="Header.TLabel").pack(anchor="w")
            ttk.Button(scrollable_frame, text="Select All in Category", 
                       command=lambda c=category: self.select_all_in_category(c)).pack(anchor="w", pady=(0, 10))
            
            for ext_id, title in extensions:
                var = tk.BooleanVar()
                self.check_vars[ext_id] = var
                # Pre-check all to default opt-in? Let's leave opt-in clear.
                var.set(False) 
                cb = tk.Checkbutton(scrollable_frame, text=title, variable=var, 
                                    bg="#1E1E1E", fg="#FFFFFF", selectcolor="#2D2D2D", 
                                    activebackground="#1E1E1E", activeforeground="#FFFFFF")
                cb.pack(anchor="w", pady=2)
                
            self.notebook.add(frame, text=category)

    def select_all_in_category(self, category):
        for ext_id, title in self.categories[category]:
            self.check_vars[ext_id].set(True)

    def install_selected(self):
        selected = [ext_id for ext_id, var in self.check_vars.items() if var.get()]
        if not selected:
            messagebox.showinfo("No Selection", "Please select at least one extension to install.")
            return

        if not os.path.exists(SUITE_DIR):
            os.makedirs(SUITE_DIR)
            
        success_count = 0
        
        # Simple progress window
        prog_win = tk.Toplevel(self.root)
        prog_win.title("Installing...")
        prog_win.geometry("400x150")
        prog_win.configure(bg="#1E1E1E")
        ttk.Label(prog_win, text="Downloading & Extracting...", style="Header.TLabel").pack(pady=10)
        prog_label = ttk.Label(prog_win, text="")
        prog_label.pack(pady=10)
        self.root.update()

        for ext_id in selected:
            prog_label.config(text=f"Installing {ext_id}...")
            prog_win.update()
            
            zip_url = f"{BASE_URL}/{ext_id}.zip"
            zip_path = os.path.join(SUITE_DIR, f"{ext_id}.zip")
            ext_dir = os.path.join(SUITE_DIR, ext_id)
            
            try:
                # Download
                req = urllib.request.Request(zip_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                    out_file.write(response.read())
                    
                # Extract
                if not os.path.exists(ext_dir):
                    os.makedirs(ext_dir)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(ext_dir)
                    
                # Clean up zip
                os.remove(zip_path)
                success_count += 1
            except Exception as e:
                print(f"Failed to install {ext_id}: {e}")
                
        prog_win.destroy()
        
        self.show_completion_guide(success_count, selected)
        
    def show_completion_guide(self, count, selected):
        guide_win = tk.Toplevel(self.root)
        guide_win.title("Installation Successful - Final Steps")
        guide_win.geometry("600x500")
        guide_win.configure(bg="#1E1E1E")
        
        text = f"""
✅ Successfully downloaded {count} extensions!

They have been securely saved to your local suite:
{SUITE_DIR}

🔥 HOW TO ACTIVATE IN CHROME / EDGE / BRAVE:
1️⃣ Open your browser and go to your extensions settings page.
   (e.g., type `chrome://extensions` in the URL bar)
2️⃣ Turn ON "Developer mode" (usually a toggle in the top right corner).
3️⃣ Click the "Load unpacked" button.
4️⃣ Navigate to the folder above and select the individual extension folder you want to load!

Because we prioritize full independence and security, these extensions run completely offline and locally from your machine, fully bypassing web store trackers.
        """
        
        msg_box = tk.Text(guide_win, bg="#1E1E1E", fg="#E5E7EB", font=("Inter", 12), wrap=tk.WORD, height=18)
        msg_box.insert(tk.END, text)
        msg_box.config(state=tk.DISABLED)
        msg_box.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        ttk.Button(guide_win, text="Got it!", command=guide_win.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
