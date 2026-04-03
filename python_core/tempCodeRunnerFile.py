import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import cyto_engine 

class CytoMetricsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CytoMetrics Pro")
        self.root.geometry("400x500")
        
        self.calib_ratio = None
        self.calib_mag = 4
        self.cell_img_path = None
        self.final_ratio = None

        # --- UI Setup (Same as before but linked) ---
        tk.Label(root, text="Step 1: Calibration", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(root, text="Upload Micrometer", command=self.load_calibration).pack()
        self.calib_label = tk.Label(root, text="Not Calibrated", fg="red")
        self.calib_label.pack()

        tk.Label(root, text="Step 2: Cell Image", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(root, text="Upload Cell Image", command=self.load_cell_image).pack()
        self.cell_label = tk.Label(root, text="No Image", fg="red")
        self.cell_label.pack()

        tk.Label(root, text="Step 3: Tools", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Button(root, text="📏 Linear Ruler", command=self.run_ruler, bg="lightblue").pack(pady=5)
        tk.Button(root, text="🔄 Lasso Tool (Coming Next)", state="disabled").pack()

    def load_calibration(self):
        path = filedialog.askopenfilename()
        if not path: return
        mag = simpledialog.askinteger("Input", "Magnification (e.g. 4)?")
        
        ratio, count = cyto_engine.calculate_calibration(path)
        if ratio and count > 10: # Safety check
            self.calib_ratio = ratio
            self.calib_mag = mag
            self.calib_label.config(text=f"Calibrated: {count} lines found\n({ratio:.4f} µm/px)", fg="green")
        else:
            messagebox.showerror("Error", f"Calibration failed! Only found {count} lines.\nCheck image lighting.")

    def load_cell_image(self):
        path = filedialog.askopenfilename()
        if not path: return
        mag = simpledialog.askinteger("Input", "Cell Magnification?")
        self.cell_img_path = path
        # Scaling Math
        self.final_ratio = self.calib_ratio * (self.calib_mag / mag)
        self.cell_label.config(text=f"Loaded: {mag}x\nFinal Ratio: {self.final_ratio:.4f} µm/px", fg="green")

    def run_ruler(self):
        if not self.cell_img_path: return
        cyto_engine.launch_ruler(self.cell_img_path, self.final_ratio)

if __name__ == "__main__":
    root = tk.Tk()
    app = CytoMetricsApp(root)
    root.mainloop()