import tkinter as tk
from tkinter import ttk, messagebox

# --- DATA REFERENSI KEBUTUHAN PAKAN HARIAN AYAM KAMPUNG (GRAM/EKOR) ---
# Data ini merupakan estimasi umum untuk ayam kampung pedaging (bukan petelur).
FEED_CONSUMPTION_PER_DAY = {
    # Umur (hari): Gram/ekor/hari
    1: 10,  2: 12,  3: 14,  4: 16,  5: 18,  6: 20,  7: 22,
    8: 24,  9: 26,  10: 28, 11: 30, 12: 32, 13: 34, 14: 36,
    15: 38, 16: 40, 17: 42, 18: 44, 19: 46, 20: 48, 21: 50,
    22: 52, 23: 54, 24: 56, 25: 58, 26: 60, 27: 62, 28: 64,
    29: 65, 30: 66, 31: 67, 32: 68, 33: 69, 34: 70, 35: 71,
    36: 72, 37: 73, 38: 74, 39: 75, 40: 76, 41: 77, 42: 78,
    43: 79, 44: 80, 45: 81, 46: 82, 47: 83, 48: 84, 49: 85,
    50: 86, 51: 87, 52: 88, 53: 89, 54: 90, 55: 91, 56: 92,
    57: 93, 58: 94, 59: 95, 60: 96, 61: 97, 62: 98, 63: 99,
    64: 100, 65: 101, 66: 102, 67: 103, 68: 104, 69: 105, 70: 106,
}

# --- FORMULA PAKAN JADI (Berdasarkan resep broiler dari dokumen) ---
# CATATAN: Resep ini tidak diubah dan merupakan asumsi untuk ayam kampung.
MAX_AGE_DATA = max(FEED_CONSUMPTION_PER_DAY.keys())
FORMULAS = {
    "STARTER": {
        "range": (1, 10),
        "composition": { "Jagung": 65.0, "Dedak Halus": 0.0, "SBM/Bungkil Kedelai": 17.5, "Tepung Ikan": 10.5, "Minyak": 2.8, "Tepung Batu": 3.5, "Topmix": 0.7 }
    },
    "GROWER": {
        "range": (11, 20),
        "composition": { "Jagung": 70.0, "Dedak Halus": 5.4, "SBM/Bungkil Kedelai": 13.5, "Tepung Ikan": 7.5, "Minyak": 0.0, "Tepung Batu": 3.0, "Topmix": 0.6 }
    },
    "FINISHER": {
        "range": (21, MAX_AGE_DATA), # Diperpanjang hingga 70 hari
        "composition": { "Jagung": 75.0, "Dedak Halus": 7.0, "SBM/Bungkil Kedelai": 10.0, "Tepung Ikan": 5.0, "Minyak": 0.0, "Tepung Batu": 2.5, "Topmix": 0.5 }
    }
}

BAHAN_BAKU = ["Jagung", "Dedak Halus", "SBM/Bungkil Kedelai", "Tepung Ikan", "Minyak", "Tepung Batu", "Topmix"]
DEFAULT_PRICES = { "Jagung": 5000, "Dedak Halus": 3000, "SBM/Bungkil Kedelai": 8500, "Tepung Ikan": 10000, "Minyak": 15000, "Tepung Batu": 1500, "Topmix": 25000 }

class FeedCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Kalkulator Total Pakan Ayam Kampung (hingga {MAX_AGE_DATA} hari)")
        self.geometry("750x680")

        self.entries = {}
        self._setup_styles()
        self._create_widgets()
        self._on_mode_change()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"))
        style.configure("TRadiobutton", font=("Segoe UI", 10))
        style.configure("TLabelFrame.Label", font=("Segoe UI", 11, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"), foreground="navy")
        style.configure("Total.TLabel", font=("Segoe UI", 12, "bold"), foreground="darkgreen")
        style.configure("Warning.TLabel", font=("Segoe UI", 8, "italic"), foreground="red")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, expand=True, pady=5)

        params_frame = ttk.LabelFrame(top_frame, text="Parameter & Mode Kalkulasi", padding="10")
        params_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(params_frame, text="Jumlah Populasi Ayam (ekor):").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,10))
        self.entries['populasi'] = ttk.Entry(params_frame, width=20)
        self.entries['populasi'].grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,15))
        
        self.calc_mode = tk.StringVar(value="total_panen")
        
        rb1 = ttk.Radiobutton(params_frame, text="Total Kebutuhan Hingga Umur Panen", variable=self.calc_mode, value="total_panen", command=self._on_mode_change)
        rb1.grid(row=2, column=0, columnspan=2, sticky="w")
        
        self.harvest_age_label = ttk.Label(params_frame, text="Umur Panen (hari):")
        self.harvest_age_label.grid(row=3, column=0, sticky="w", padx=(20,5), pady=2)
        self.entries['umur_panen'] = ttk.Entry(params_frame, width=10)
        self.entries['umur_panen'].grid(row=3, column=1, sticky="w", pady=2)
        
        max_age_str = f"(Maks. {MAX_AGE_DATA} hari)"
        ttk.Label(params_frame, text=max_age_str, font=("Segoe UI", 8, "italic")).grid(row=3, column=2, sticky="w")

        rb2 = ttk.Radiobutton(params_frame, text="Kebutuhan per Fase", variable=self.calc_mode, value="per_fase", command=self._on_mode_change)
        rb2.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,0))

        self.phase_label = ttk.Label(params_frame, text="Pilih Fase:")
        self.phase_label.grid(row=5, column=0, sticky="w", padx=(20,5), pady=2)
        phase_values = ["STARTER (1-10)", "GROWER (11-20)", f"FINISHER (21-{MAX_AGE_DATA})"]
        self.phase_var = tk.StringVar()
        self.phase_menu = ttk.Combobox(params_frame, textvariable=self.phase_var, values=phase_values, state="readonly")
        self.phase_menu.grid(row=5, column=1, columnspan=2, sticky="ew", pady=2)
        
        prices_frame = ttk.LabelFrame(top_frame, text="Harga Bahan Baku (Rp/Kg)", padding="10")
        prices_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        for i, material in enumerate(BAHAN_BAKU):
            ttk.Label(prices_frame, text=f"{material}:").grid(row=i, column=0, sticky="w", pady=3)
            entry = ttk.Entry(prices_frame, width=15)
            entry.insert(0, str(DEFAULT_PRICES.get(material, 0)))
            entry.grid(row=i, column=1, sticky="ew")
            self.entries[material] = entry

        calc_button = ttk.Button(main_frame, text="HITUNG TOTAL KEBUTUHAN", command=self.calculate)
        calc_button.pack(pady=10, fill=tk.X)

        self.result_info_label = ttk.Label(main_frame, text="Hasil Perhitungan:", style="Header.TLabel")
        self.result_info_label.pack(pady=(0, 2))
        
        ttk.Label(main_frame, text="*Formula pakan adalah estimasi berdasarkan resep broiler.", style="Warning.TLabel").pack(pady=(0, 5))

        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)
        columns = ("material", "kebutuhan", "harga_kg", "total_biaya")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        self.tree.heading("material", text="Bahan Baku"); self.tree.heading("kebutuhan", text="Total Kebutuhan (Kg)"); self.tree.heading("harga_kg", text="Harga/Kg (Rp)"); self.tree.heading("total_biaya", text="Total Biaya (Rp)")
        self.tree.column("material", width=200, anchor=tk.W); self.tree.column("kebutuhan", width=150, anchor=tk.E); self.tree.column("harga_kg", width=150, anchor=tk.E); self.tree.column("total_biaya", width=180, anchor=tk.E)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.grand_total_label = ttk.Label(main_frame, text="Grand Total Biaya: Rp 0", style="Total.TLabel", padding=(0,5,0,5))
        self.grand_total_label.pack(anchor=tk.E)

    def _on_mode_change(self):
        mode = self.calc_mode.get()
        if mode == "total_panen":
            self.entries['umur_panen'].config(state="normal")
            self.harvest_age_label.config(state="normal")
            self.phase_menu.config(state="disabled")
            self.phase_label.config(state="disabled")
        else:
            self.entries['umur_panen'].config(state="disabled")
            self.harvest_age_label.config(state="disabled")
            self.phase_menu.config(state="readonly")
            self.phase_label.config(state="normal")
            self.phase_menu.set(self.phase_menu['values'][0])

    def calculate(self):
        try:
            populasi = int(self.entries['populasi'].get())
            prices = {m: float(self.entries[m].get()) for m in BAHAN_BAKU}
            mode = self.calc_mode.get()
            
            start_day, end_day = 0, 0
            info_text = ""

            if mode == "total_panen":
                end_day = int(self.entries['umur_panen'].get())
                start_day = 1
                if not (1 <= end_day <= MAX_AGE_DATA):
                    raise ValueError(f"Umur Panen harus antara 1 dan {MAX_AGE_DATA} hari.")
                info_text = f"Total Kebutuhan dari Umur 1 hingga {end_day} Hari"
            else:
                phase_choice_str = self.phase_var.get()
                phase_choice = phase_choice_str.split(" ")[0]
                start_day, end_day_raw = FORMULAS[phase_choice]['range']
                end_day = MAX_AGE_DATA if phase_choice == "FINISHER" else end_day_raw
                info_text = f"Total Kebutuhan Fase {phase_choice} (Umur {start_day}-{end_day} Hari)"

            total_material_needs = {material: 0 for material in BAHAN_BAKU}
            
            for day in range(start_day, end_day + 1):
                daily_feed_per_chicken_g = FEED_CONSUMPTION_PER_DAY[day]
                total_feed_for_day_kg = (populasi * daily_feed_per_chicken_g) / 1000.0
                
                if FORMULAS["STARTER"]["range"][0] <= day <= FORMULAS["STARTER"]["range"][1]: current_phase = "STARTER"
                elif FORMULAS["GROWER"]["range"][0] <= day <= FORMULAS["GROWER"]["range"][1]: current_phase = "GROWER"
                else: current_phase = "FINISHER"
                
                composition = FORMULAS[current_phase]["composition"]
                for material, percentage in composition.items():
                    material_needed_kg = total_feed_for_day_kg * (percentage / 100.0)
                    total_material_needs[material] += material_needed_kg

            self.result_info_label.config(text=info_text)
            for item in self.tree.get_children(): self.tree.delete(item)
            
            grand_total_cost = 0
            for material in BAHAN_BAKU:
                total_kg = total_material_needs[material]
                if total_kg > 0:
                    harga_kg = prices[material]
                    total_cost = total_kg * harga_kg
                    grand_total_cost += total_cost
                    self.tree.insert("", tk.END, values=(material, f"{total_kg:,.2f}", f"{harga_kg:,.0f}", f"{total_cost:,.2f}"))
            
            self.grand_total_label.config(text=f"Grand Total Biaya: Rp {grand_total_cost:,.2f}")

        except (ValueError, KeyError) as e:
            messagebox.showerror("Error Input", f"Input tidak valid. Pastikan semua angka benar.\n\nDetail: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    app = FeedCalculatorApp()
    app.mainloop()