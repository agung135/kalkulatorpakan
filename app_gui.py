# app_gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from PIL import Image, ImageTk

# Mengimpor modul-modul proyek
import config
import data_manager
from gui_windows import FormulaManagerWindow, BahanBakuManagerWindow
from gui_dashboard import DashboardWindow
from optimizer import cari_formula_termurah

class KalkulatorPakanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kalkulator Pakan V8.0 by Pa-ri (Pertanian Mandiri)")
        self.geometry("1300x850")
        
        self.setup_theme()
        try:
            if os.path.exists(config.LOGO_FILE):
                self.logo_tk = ImageTk.PhotoImage(Image.open(config.LOGO_FILE))
                self.iconphoto(True, self.logo_tk)
        except Exception as e:
            print(f"Gagal memuat logo: {e}")

        # Inisialisasi atribut dari config
        self.protein_ideal = config.PROTEIN_IDEAL
        self.distribusi_pakan = config.DISTRIBUSI_PAKAN
        self.rasio_konsentrat = config.RASIO_KONSENTRAT
        self.umur_fase = config.UMUR_FASE
        
        # Dictionary untuk menyimpan data dan widget
        self.bahan_entries = {}
        self.target_entries = {}
        self.stock_entries = {}
        self.formulas = {}
        self.bahan_baku = {}

        # Memuat data saat aplikasi dimulai
        self.load_bahan_baku()
        self.load_formulas()
        self.create_widgets()
        self.load_stock_data()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_theme(self):
        s = ttk.Style(self); s.theme_use('clam')
        s.configure('.', background=config.BG_COLOR, foreground=config.TEXT_COLOR, font=('Helvetica', 9))
        s.configure('TFrame', background=config.BG_COLOR)
        s.configure('TLabel', background=config.BG_COLOR, foreground=config.TEXT_COLOR)
        s.configure('TButton', background='#E0E0E0', foreground=config.TEXT_COLOR, borderwidth=1)
        s.map('TButton', background=[('active', '#C0C0C0')])
        s.configure("Accent.TButton", foreground='white', background=config.ACCENT_COLOR, font=('Helvetica', 9, 'bold'))
        s.map('Accent.TButton', background=[('active', '#85AC2F')])
        s.configure('TLabelFrame', background=config.BG_COLOR, bordercolor=config.ACCENT_COLOR)
        s.configure('TLabelFrame.Label', background=config.BG_COLOR, foreground=config.ACCENT_COLOR, font=('Helvetica', 10, 'bold'))
        s.configure('TEntry', fieldbackground=config.INPUT_BG, foreground=config.TEXT_COLOR)
        s.configure('TCombobox', fieldbackground=config.INPUT_BG, foreground=config.TEXT_COLOR)
        self.option_add('*TCombobox*Listbox.background', config.INPUT_BG)
        self.option_add('*TCombobox*Listbox.foreground', config.TEXT_COLOR)
        s.configure('TNotebook.Tab', font=('Helvetica', 10, 'bold'), padding=[10, 5])
        s.map("TNotebook.Tab", background=[("selected", config.ACCENT_COLOR)], foreground=[("selected", "white")])
        s.configure('TNotebook', background=config.BG_COLOR)

    def create_widgets(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Simpan Sesi", command=self.save_session)
        file_menu.add_command(label="Muat Sesi", command=self.load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Keluar", command=self.on_closing)
        menu_bar.add_cascade(label="File", menu=file_menu)

        report_menu = tk.Menu(menu_bar, tearoff=0)
        report_menu.add_command(label="Buka Dasbor Analisis", command=self.open_dashboard)
        menu_bar.add_cascade(label="Laporan", menu=report_menu)
        
        self.config(menu=menu_bar)

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        left_container = ttk.Frame(main_frame)
        left_container.grid(row=0, column=0, sticky="nsew")
        left_container.rowconfigure(0, weight=1)
        left_container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0, background=config.BG_COLOR)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame = ttk.Frame(canvas, padding="10")
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.db_frame = ttk.LabelFrame(self.scrollable_frame, text="1. Database Bahan Baku", padding="10")
        self.db_frame.pack(fill=tk.X, expand=True, pady=5)
        self.stock_frame = ttk.LabelFrame(self.scrollable_frame, text="2. Stok Gudang (kg)", padding="10")
        self.stock_frame.pack(fill=tk.X, expand=True, pady=10)
        
        action_notebook = ttk.Notebook(self.scrollable_frame)
        action_notebook.pack(fill=tk.X, expand=True, pady=5)
        optimizer_tab = ttk.Frame(action_notebook, padding=10)
        action_notebook.add(optimizer_tab, text='Optimizer Cerdas')
        manual_tab = ttk.Frame(action_notebook, padding=10)
        action_notebook.add(manual_tab, text='Analisis Manual')

        target_frame = ttk.LabelFrame(optimizer_tab, text="Target Nutrisi Pakan Jadi", padding="10")
        target_frame.pack(fill=tk.X, expand=True)
        targets = {"pk_min":"PK Min (%)", "em_min":"EM Min (kkal/kg)", "ca_min":"Ca Min (%)", "p_min":"P Min (%)", "sk_max":"SK Max (%)"}
        for i, (key, label) in enumerate(targets.items()):
            ttk.Label(target_frame, text=label + ":").grid(row=i, column=0, padx=5, pady=3, sticky='w')
            entry = ttk.Entry(target_frame, width=15)
            entry.insert(0, str(config.TARGET_NUTRISI_DEFAULT.get(key, 0.0)))
            entry.grid(row=i, column=1, padx=5, pady=3)
            self.target_entries[key] = entry
        ttk.Button(target_frame, text="Cari Formula Termurah >>", command=self.run_optimizer, style="Accent.TButton").grid(row=len(targets), column=0, columnspan=2, pady=10)

        input_frame = ttk.LabelFrame(manual_tab, text="Data Pemeliharaan", padding="10")
        input_frame.pack(fill=tk.X, expand=True, pady=5)
        formula_choice_frame = ttk.LabelFrame(manual_tab, text="Pilihan Formula per Fase", padding="10")
        formula_choice_frame.pack(fill=tk.X, expand=True, pady=10)
        button_frame = ttk.Frame(manual_tab, padding=10)
        button_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Label(input_frame, text="Jumlah Ekor Ayam:").grid(row=0, column=0)
        self.jumlah_ayam_entry = ttk.Entry(input_frame, width=15)
        self.jumlah_ayam_entry.grid(row=0, column=1, padx=5)
        ttk.Label(input_frame, text="Total Pakan /Ekor (Kg):").grid(row=1, column=0)
        self.total_pakan_entry = ttk.Entry(input_frame, width=15)
        self.total_pakan_entry.insert(0, "4.5")
        self.total_pakan_entry.grid(row=1, column=1, padx=5)
        
        self.formula_combos = {}
        for i, fase in enumerate(['Starter', 'Grower', 'Finisher']):
            ttk.Label(formula_choice_frame, text=f"Fase {fase}:").grid(row=i, column=0, sticky='w')
            combo = ttk.Combobox(formula_choice_frame, state="readonly")
            combo.grid(row=i, column=1, sticky='ew')
            self.formula_combos[fase] = combo
        
        ttk.Button(formula_choice_frame, text="Kelola Formula...", command=self.open_formula_manager).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Hitung & Analisa Manual", command=self.calculate_all).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Kurangi Stok & Catat di Log", command=self.calculate_and_update_stock).pack(fill=tk.X, pady=2)
        
        credit_label = ttk.Label(self.scrollable_frame, text="Dibuat oleh: Pari", font=('Helvetica', 8, 'italic'))
        credit_label.pack(side=tk.BOTTOM, pady=(15, 0))
        
        hasil_frame = ttk.LabelFrame(main_frame, text="Hasil", padding="10")
        hasil_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0))
        
        self.notebook = ttk.Notebook(hasil_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.optimizer_tab_hasil = ttk.Frame(self.notebook, padding=10)
        self.manual_tab_hasil = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.optimizer_tab_hasil, text="Hasil Optimizer")
        self.notebook.add(self.manual_tab_hasil, text="Hasil Analisis Manual")

        self.optimizer_text = tk.Text(self.optimizer_tab_hasil, wrap="word", state="disabled", font=("Courier", 10), background=config.INPUT_BG, foreground=config.TEXT_COLOR)
        self.optimizer_text.pack(fill=tk.BOTH, expand=True)
        self.manual_text = tk.Text(self.manual_tab_hasil, wrap="word", state="disabled", font=("Courier", 10), background=config.INPUT_BG, foreground=config.TEXT_COLOR)
        self.manual_text.pack(fill=tk.BOTH, expand=True)
        
        print_button = ttk.Button(hasil_frame, text="Cetak Tab Aktif (PDF)", command=self.print_to_pdf)
        print_button.pack(pady=10)
        
        for text_widget in [self.optimizer_text, self.manual_text]:
            text_widget.tag_configure("deficit", foreground="#E53935", font=("Courier", 10, "bold"))
            text_widget.tag_configure("sufficient", foreground="#006400", font=("Courier", 10, "bold"))
            text_widget.tag_configure("total_cost", font=("Courier", 10, "bold"))
        
        # Panggil refresh setelah semua kerangka widget utama dibuat
        self.refresh_ui_panels()

    def refresh_ui_panels(self):
        for widget in self.db_frame.winfo_children(): widget.destroy()
        for widget in self.stock_frame.winfo_children(): widget.destroy()
        self.bahan_entries.clear()
        self.stock_entries.clear()

        headers = ["Nama Bahan", "Harga/Kg", "% PK", "EM", "Ca", "P", "SK"]
        for col, header in enumerate(headers):
            ttk.Label(self.db_frame, text=header, font=('Helvetica', 9, 'bold')).grid(row=0, column=col, padx=5, sticky='w')
        
        sorted_materials = sorted(self.bahan_baku.keys())
        for row, bahan in enumerate(sorted_materials, 1):
            ttk.Label(self.db_frame, text=f"{bahan}:").grid(row=row, column=0, padx=5, pady=3, sticky='w')
            self.bahan_entries[bahan] = {}
            for col, key in enumerate(['harga', 'pk', 'em', 'ca', 'p', 'sk'], 1):
                entry = ttk.Entry(self.db_frame, width=10)
                entry.insert(0, str(self.bahan_baku[bahan].get(key, 0.0)))
                entry.grid(row=row, column=col, padx=5, pady=3)
                self.bahan_entries[bahan][key] = entry
        
        ttk.Button(self.db_frame, text="Kelola Bahan Baku...", command=self.open_bahan_baku_manager).grid(row=len(sorted_materials) + 1, column=0, columnspan=len(headers), pady=10)

        for i, bahan in enumerate(sorted_materials):
            ttk.Label(self.stock_frame, text=f"{bahan}:").grid(row=i, column=0, sticky='w')
            e_stok = ttk.Entry(self.stock_frame, width=15)
            e_stok.insert(0, "0")
            e_stok.grid(row=i, column=1, padx=5, pady=2)
            self.stock_entries[bahan] = e_stok
        
        self.load_stock_data()
        self.refresh_formula_combos()

    def load_bahan_baku(self):
        self.bahan_baku = data_manager.load_json(config.BAHAN_BAKU_FILE, config.BAHAN_BAKU_DEFAULT)

    def save_bahan_baku(self):
        data_manager.save_json(config.BAHAN_BAKU_FILE, self.bahan_baku)

    def open_bahan_baku_manager(self):
        BahanBakuManagerWindow(self)

    def load_formulas(self):
        self.formulas = data_manager.load_json(config.FORMULA_FILE, config.FORMULA_DEFAULT)

    def save_formulas(self):
        data_manager.save_json(config.FORMULA_FILE, self.formulas)

    def refresh_formula_combos(self):
        formula_names = list(self.formulas.keys())
        for combo in self.formula_combos.values():
            current = combo.get()
            combo['values'] = formula_names
            if current in formula_names:
                combo.set(current)
            elif formula_names:
                combo.set(formula_names[0])
            else:
                combo.set("")
        for fase, combo in self.formula_combos.items():
            default_selection = next((name for name in formula_names if fase in name), formula_names[0] if formula_names else "")
            combo.set(default_selection)

    def open_formula_manager(self):
        FormulaManagerWindow(self)

    def on_closing(self):
        self.save_stock_data()
        self.destroy()

    def save_stock_data(self):
        stock_data = {bahan: entry.get() for bahan, entry in self.stock_entries.items() if bahan in self.stock_entries}
        data_manager.save_json(config.STOCK_FILE, stock_data)

    def load_stock_data(self):
        stock_data = data_manager.load_json(config.STOCK_FILE, {})
        for bahan, val in stock_data.items():
            if bahan in self.stock_entries:
                self.stock_entries[bahan].delete(0, tk.END)
                self.stock_entries[bahan].insert(0, val)

    def save_session(self):
        try:
            filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Simpan Sesi Sebagai...")
            if not filepath: return
            db_data = {b: {k: e.get() for k, e in v.items()} for b, v in self.bahan_entries.items()}
            session_data = {
                'database_bahan_baku': db_data, 
                'stok': {b: e.get() for b, e in self.stock_entries.items()}, 
                'jumlah_ayam': self.jumlah_ayam_entry.get(), 
                'total_pakan': self.total_pakan_entry.get(), 
                'formula_pilihan': {f: c.get() for f, c in self.formula_combos.items()}, 
                'target_nutrisi': {t: e.get() for t, e in self.target_entries.items()}
            }
            data_manager.save_json(filepath, session_data)
            messagebox.showinfo("Sukses", f"Sesi berhasil disimpan di:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan sesi:\n{e}")

    def load_session(self):
        try:
            filepath = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")], title="Pilih File Sesi untuk Dimuat")
            if not filepath: return
            session_data = data_manager.load_json(filepath)
            
            db_data = session_data.get('database_bahan_baku', {})
            if db_data:
                self.bahan_baku = {bahan: {k:v for k,v in data.items()} for bahan, data in db_data.items()}
                self.save_bahan_baku()
                self.refresh_ui_panels()

            for d, e_dict in [(session_data.get('stok',{}), self.stock_entries), (session_data.get('target_nutrisi', {}), self.target_entries)]:
                for b, v in d.items():
                    if b in e_dict:
                        e_dict[b].delete(0, tk.END)
                        e_dict[b].insert(0, v)
            
            self.jumlah_ayam_entry.delete(0, tk.END)
            self.jumlah_ayam_entry.insert(0, session_data.get('jumlah_ayam', ''))
            self.total_pakan_entry.delete(0, tk.END)
            self.total_pakan_entry.insert(0, session_data.get('total_pakan', ''))
            
            self.refresh_formula_combos()
            for f, fname in session_data.get('formula_pilihan', {}).items():
                if f in self.formula_combos:
                    self.formula_combos[f].set(fname)
            
            messagebox.showinfo("Sukses", f"Sesi berhasil dimuat dari:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memuat sesi:\n{e}")

    def print_to_pdf(self):
        tab_index = self.notebook.index(self.notebook.select())
        report_text = self.optimizer_text.get("1.0", tk.END) if tab_index == 0 else self.manual_text.get("1.0", tk.END)
        if not report_text.strip():
            messagebox.showwarning("Peringatan", "Tidak ada hasil di tab ini untuk dicetak.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")], title="Simpan Laporan Sebagai PDF", initialfile=f"Laporan Pakan - {datetime.now().strftime('%Y-%m-%d')}.pdf")
        if filepath:
            data_manager.print_to_pdf(filepath, report_text)
    
    def open_dashboard(self):
        DashboardWindow(self)

    def log_activity(self, tipe, nama_resep, data, db=None):
        log_entry = {"tanggal": datetime.now().isoformat(), "tipe": tipe, "nama_resep": nama_resep}
        
        if tipe == "Optimizer":
            try:
                total_kg_str = tk.simpledialog.askstring("Input Kuantitas", "Berapa total kg pakan yang akan dibuat dari resep ini?", parent=self)
                total_kg = float(total_kg_str) if total_kg_str else 0
            except (ValueError, TypeError):
                total_kg = 0

            if total_kg <= 0:
                messagebox.showwarning("Batal", "Pencatatan dibatalkan.")
                return

            rincian_bahan = {bahan: {'kg': total_kg * (persen/100), 'biaya': total_kg * (persen/100) * db[bahan]['harga']} for bahan, persen in data.items()}
            total_biaya = sum(d['biaya'] for d in rincian_bahan.values())
            log_entry.update({"jumlah_kg": total_kg, "total_biaya": total_biaya, "rincian_bahan": rincian_bahan})

            for bahan, rincian in rincian_bahan.items():
                if bahan in self.stock_entries:
                    stok_awal = float(self.stock_entries[bahan].get() or 0)
                    stok_akhir = max(0, stok_awal - rincian['kg'])
                    self.stock_entries[bahan].delete(0, tk.END)
                    self.stock_entries[bahan].insert(0, f"{stok_akhir:.2f}")
            
            self.save_stock_data()
            messagebox.showinfo("Sukses", "Stok gudang telah dikurangi dan aktivitas dicatat.")

        elif tipe == "Manual":
            log_entry.update(data)
        
        data_manager.append_to_log(log_entry)
        if tipe == "Manual":
             messagebox.showinfo("Sukses", "Aktivitas berhasil dicatat di buku log.")

    def run_optimizer(self):
        try:
            database = {b: {k: float(e.get()) for k, e in v.items()} for b, v in self.bahan_entries.items()}
            targets = {k: float(e.get()) for k, e in self.target_entries.items()}
        except ValueError:
            messagebox.showerror("Error Input", "Pastikan semua nilai di Database dan Target adalah angka.")
            return
        
        self.notebook.select(self.optimizer_tab_hasil)
        resep, biaya, status = cari_formula_termurah(database, targets)
        self.display_optimizer_results(resep, biaya, status, database)

    def display_optimizer_results(self, resep, biaya, status, db):
        if hasattr(self, 'btn_log_optimizer'): self.btn_log_optimizer.destroy()
        widget = self.optimizer_text
        widget.config(state="normal"); widget.delete('1.0', tk.END)
        widget.insert(tk.END, f"--- HASIL OPTIMASI FORMULA ---\n\n")
        widget.insert(tk.END, f"Status Perhitungan: {status}\n\n", "sufficient" if status == "Optimal" else "deficit")
        
        if status == "Optimal":
            widget.insert(tk.END, f"Biaya Pakan per Kg: Rp {biaya:,.2f}\n", "total_cost")
            widget.insert(tk.END, "\n--- KOMPOSISI RESEP TERMURAH ---\n")
            for bahan, persen in sorted(resep.items()):
                widget.insert(tk.END, f"- {bahan:<20}: {persen:.2f} %\n")
            
            hasil_nutrisi = { "pk": 0, "em": 0, "ca": 0, "p": 0, "sk": 0 }
            for bahan, persen in resep.items():
                for nutrisi in hasil_nutrisi:
                    hasil_nutrisi[nutrisi] += db[bahan][nutrisi] * (persen / 100)
            
            widget.insert(tk.END, "\n--- ANALISIS NUTRISI HASIL ---\n")
            widget.insert(tk.END, f"- Protein Kasar : {hasil_nutrisi['pk']:.2f} %\n")
            widget.insert(tk.END, f"- Energi Metabolis: {hasil_nutrisi['em']:.0f} kkal/kg\n")
            widget.insert(tk.END, f"- Kalsium         : {hasil_nutrisi['ca']:.2f} %\n")
            widget.insert(tk.END, f"- Fosfor          : {hasil_nutrisi['p']:.2f} %\n")
            widget.insert(tk.END, f"- Serat Kasar     : {hasil_nutrisi['sk']:.2f} %\n")
            
            self.btn_log_optimizer = ttk.Button(self.optimizer_tab_hasil, text="Buat Pakan & Catat di Log", command=lambda: self.log_activity("Optimizer", "Resep Optimal Cerdas", resep, db=db), style="Accent.TButton")
            self.btn_log_optimizer.pack(pady=10)
        else:
            widget.insert(tk.END, "Tidak ditemukan solusi yang optimal.\n")
            widget.insert(tk.END, "Saran: Periksa target Anda (mungkin terlalu tinggi/rendah)\n")
            widget.insert(tk.END, "atau periksa nilai nutrisi di database bahan baku.")
            
        widget.config(state="disabled")

    def get_manual_inputs(self):
        try:
            stocks = {b: float(e.get()) for b, e in self.stock_entries.items()}
            proteins = {b: float(v['pk'].get()) for b, v in self.bahan_entries.items()}
            prices = {b: float(v['harga'].get()) for b, v in self.bahan_entries.items()}
            jumlah_ayam = int(self.jumlah_ayam_entry.get() or 0)
            total_pakan_per_ekor = float(self.total_pakan_entry.get() or 0.0)
            return prices, proteins, stocks, jumlah_ayam, total_pakan_per_ekor
        except (ValueError, KeyError) as e:
            messagebox.showerror("Error Input", f"Pastikan semua input angka valid. Error pada: {e}")
            return None, None, None, None, None

    def calculate_and_update_stock(self):
        prices, proteins, stocks, jumlah_ayam, total_pakan_per_ekor, kebutuhan_bahan, total_biaya = self.calculate_all(return_needs=True)
        if kebutuhan_bahan is None: return
        
        if messagebox.askyesno("Konfirmasi", "Yakin ingin mengurangi stok sesuai hasil Analisis Manual ini dan mencatatnya di log?"):
            for bahan, butuh in kebutuhan_bahan.items():
                if bahan in self.stock_entries:
                    stok_saat_ini = stocks.get(bahan, 0)
                    stok_baru = max(0, stok_saat_ini - butuh)
                    self.stock_entries[bahan].delete(0, tk.END); self.stock_entries[bahan].insert(0, f"{stok_baru:.2f}")
            
            rincian_log = {'jumlah_kg': sum(kebutuhan_bahan.values()), 'total_biaya': total_biaya, 'rincian_bahan': {b: {'kg': kg, 'biaya': kg * prices.get(b,0)} for b, kg in kebutuhan_bahan.items()}}
            self.log_activity("Manual", "Analisis Kebutuhan Ternak", rincian_log)
            self.save_stock_data()
            self.calculate_all()
    
    def calculate_all(self, return_needs=False):
        prices, proteins, stocks, jumlah_ayam, total_pakan_per_ekor = self.get_manual_inputs()
        if prices is None: return (None, None, None, None, None, None, None) if return_needs else None
        
        protein_carrier = (proteins.get('Jagung Giling',0) * 0.7) + (proteins.get('Dedak Bekatul',0) * 0.3)
        detail_per_fase, kebutuhan_total_bahan = {}, {bahan: 0 for bahan in self.bahan_baku.keys()}
        
        if jumlah_ayam > 0 and total_pakan_per_ekor > 0:
            for fase in ['Starter', 'Grower', 'Finisher']:
                selected_formula_name = self.formula_combos[fase].get()
                if not selected_formula_name or selected_formula_name not in self.formulas:
                    messagebox.showerror("Error", f"Pilih formula yang valid untuk fase {fase}.")
                    return (None, None, None, None, None, None, None) if return_needs else None
                
                current_formula = self.formulas[selected_formula_name]
                biaya_carrier_per_kg = (prices.get('Jagung Giling',0) * 0.7) + (prices.get('Dedak Bekatul',0) * 0.3)
                biaya_konsentrat_per_kg = sum(current_formula.get(b, 0) * prices.get(b, 0) for b in current_formula) / 100
                protein_konsentrat = sum(current_formula.get(b, 0) * proteins.get(b, 0) for b in current_formula) / 100
                pk_pakan_jadi = (protein_konsentrat * self.rasio_konsentrat[fase]) + (protein_carrier * (1 - self.rasio_konsentrat[fase]))
                deficit = pk_pakan_jadi - self.protein_ideal[fase]
                rekomendasi = "Tambah sumber protein tinggi" if deficit < 0 else "Kebutuhan Protein Cukup"
                pakan_jadi_per_ekor = total_pakan_per_ekor * self.distribusi_pakan[fase]
                total_pakan_jadi_populasi = jumlah_ayam * pakan_jadi_per_ekor
                total_konsentrat_populasi = total_pakan_jadi_populasi * self.rasio_konsentrat[fase]
                total_carrier_populasi = total_pakan_jadi_populasi - total_konsentrat_populasi
                biaya_fase = (total_konsentrat_populasi * biaya_konsentrat_per_kg) + (total_carrier_populasi * biaya_carrier_per_kg)
                detail_per_fase[fase] = {'pk_pakan_jadi': pk_pakan_jadi, 'deficit': deficit, 'rekomendasi': rekomendasi, 'umur': self.umur_fase[fase], 'pakan_per_ekor': pakan_jadi_per_ekor, 'total_pakan_jadi': total_pakan_jadi_populasi, 'total_konsentrat': total_konsentrat_populasi, 'total_carrier': total_carrier_populasi, 'biaya_fase': biaya_fase}
                
                for bahan, kg_per_100 in current_formula.items():
                    if bahan in kebutuhan_total_bahan: kebutuhan_total_bahan[bahan] += total_konsentrat_populasi * (kg_per_100 / 100)
            
            total_carrier_kg = sum(detail.get('total_carrier', 0) for detail in detail_per_fase.values())
            if 'Jagung Giling' in kebutuhan_total_bahan: kebutuhan_total_bahan['Jagung Giling'] += total_carrier_kg * 0.7
            if 'Dedak Bekatul' in kebutuhan_total_bahan: kebutuhan_total_bahan['Dedak Bekatul'] += total_carrier_kg * 0.3
        
        total_biaya = sum(kebutuhan_total_bahan.get(b, 0) * prices.get(b, 0) for b in kebutuhan_total_bahan)
        
        if return_needs:
            return prices, proteins, stocks, jumlah_ayam, total_pakan_per_ekor, kebutuhan_total_bahan, total_biaya
        
        self.display_manual_results(detail_per_fase, kebutuhan_total_bahan, stocks, jumlah_ayam, total_biaya)

    def display_manual_results(self, detail_per_fase, kebutuhan_bahan, stocks, jumlah_ayam, total_biaya):
        self.notebook.select(self.manual_tab_hasil)
        widget = self.manual_text
        widget.config(state="normal"); widget.delete('1.0', tk.END)
        widget.insert(tk.END, f"--- ANALISIS MANUAL UNTUK {jumlah_ayam} EKOR ---\n\n")
        if jumlah_ayam > 0 and detail_per_fase:
            for fase, detail in detail_per_fase.items():
                selected_formula = self.formula_combos[fase].get()
                widget.insert(tk.END, f" Fase {fase.upper()} (Menggunakan: {selected_formula})\n")
                widget.insert(tk.END, "--------------------------------------------------\n")
                deficit_text = f"({detail['deficit']:.2f} %)"
                widget.insert(tk.END, f"  - Protein Pakan Jadi   : {detail['pk_pakan_jadi']:.2f} % (Target: {self.protein_ideal[fase]:.1f} %)\n")
                widget.insert(tk.END, "  - Analisis Kebutuhan   : ")
                widget.insert(tk.END, f"{'KEKURANGAN' if detail['deficit'] < 0 else 'CUKUP'} {deficit_text}\n", "deficit" if detail['deficit'] < 0 else "sufficient")
                widget.insert(tk.END, f"  - Rekomendasi          : {detail['rekomendasi']}\n")
                widget.insert(tk.END, f"  - Rincian Campuran Total:\n")
                widget.insert(tk.END, f"    > Konsentrat         : {detail['total_konsentrat']:.2f} kg\n")
                widget.insert(tk.END, f"    > Jagung/Dedak       : {detail['total_carrier']:.2f} kg\n")
                widget.insert(tk.END, f"  - Estimasi Biaya Fase  : Rp {detail['biaya_fase']:,.2f}\n\n", "total_cost")
            widget.insert(tk.END, "--- REKAPITULASI KEBUTUHAN & STATUS STOK ---\n")
            header = f"{'Bahan Baku':<22}{'Dibutuhkan':>12}{'Stok':>12}{'Status':>16}\n"
            widget.insert(tk.END, header); widget.insert(tk.END, "-"*len(header) + "\n")
            for bahan in sorted(kebutuhan_bahan.keys()):
                if kebutuhan_bahan[bahan] > 0:
                    butuh, stok = kebutuhan_bahan[bahan], stocks.get(bahan, 0)
                    selisih, status = butuh - stok, "CUKUP" if (butuh - stok) <= 0 else f"BELI {(butuh - stok):.2f} kg"
                    line = f"{bahan:<22}{butuh:>12.2f} kg{stok:>12.2f} kg"
                    widget.insert(tk.END, line)
                    widget.insert(tk.END, f"{status:>16}\n", "sufficient" if selisih <= 0 else "deficit")
            widget.insert(tk.END, "\n--- ESTIMASI TOTAL BIAYA KESELURUHAN ---\n")
            widget.insert(tk.END, f"  Rp {total_biaya:,.2f}\n", "total_cost")
            widget.insert(tk.END, "\n" + "="*59 + "\n")
            widget.insert(tk.END, "*Catatan: Perhitungan protein mengasumsikan carrier\n terdiri dari 70% Jagung dan 30% Dedak.")
        else:
            widget.insert(tk.END, "Masukkan jumlah ayam dan total pakan per ekor (> 0)\nuntuk melihat detail kebutuhan.\n")
        widget.config(state="disabled")