import tkinter as tk
from tkinter import ttk, messagebox
import config

class FormulaManagerWindow(tk.Toplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.title("Manajer Formula")
        self.geometry("500x400")
        self.transient(parent_app)
        self.grab_set()

        list_frame = ttk.Frame(self, padding=10); list_frame.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame); self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.refresh_listbox()

        btn_frame = ttk.Frame(self, padding=10); btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Tambah Baru", command=self.add_formula).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Edit Pilihan", command=self.edit_formula).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Hapus Pilihan", command=self.delete_formula).pack(side=tk.LEFT, expand=True, padx=5)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for name in sorted(self.parent_app.formulas.keys()):
            self.listbox.insert(tk.END, name)

    def add_formula(self):
        FormulaEditorWindow(self, None, self.refresh_listbox)

    def edit_formula(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        formula_name = self.listbox.get(selected_indices[0])
        FormulaEditorWindow(self, formula_name, self.refresh_listbox)

    def delete_formula(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        name = self.listbox.get(selected_indices[0])
        if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus formula '{name}'?"):
            del self.parent_app.formulas[name]
            self.parent_app.save_formulas()
            self.refresh_listbox()
            self.parent_app.refresh_formula_combos()

class FormulaEditorWindow(tk.Toplevel):
    def __init__(self, parent_manager, formula_name, refresh_callback):
        super().__init__(parent_manager)
        self.parent_manager = parent_manager
        self.parent_app = parent_manager.parent_app
        self.formula_name = formula_name
        self.refresh_callback = refresh_callback

        self.title(f"Editor Formula: {formula_name or 'Baru'}")
        self.geometry("600x500")
        self.transient(parent_manager)
        self.grab_set()

        header_frame = ttk.Frame(self, padding=10); header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Nama Formula:").pack(side=tk.LEFT, padx=5)
        self.name_entry = ttk.Entry(header_frame); self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if formula_name: self.name_entry.insert(0, formula_name)

        canvas = tk.Canvas(self, borderwidth=0); canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        self.ing_frame = ttk.Frame(canvas, padding=10)
        canvas.create_window((0, 0), window=self.ing_frame, anchor="nw")
        
        self.ingredients = []
        
        if formula_name:
            for bahan, persen in self.parent_app.formulas[formula_name].items():
                self.add_ingredient_row(bahan, persen)
        else:
            for _ in range(5): self.add_ingredient_row()

        btn_frame = ttk.Frame(self, padding=10); btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_frame, text="Tambah Bahan", command=self.add_ingredient_row).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Simpan Formula", command=self.save_formula).pack(side=tk.RIGHT, padx=10)

        self.ing_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def add_ingredient_row(self, bahan=None, persen=None):
        row = len(self.ingredients)
        # Mengambil daftar bahan baku dinamis dari aplikasi utama
        bahan_list = sorted(self.parent_app.bahan_baku.keys())
        combo = ttk.Combobox(self.ing_frame, values=bahan_list, state="readonly")
        combo.grid(row=row, column=0, padx=5, pady=2)
        if bahan: combo.set(bahan)
        
        entry = ttk.Entry(self.ing_frame, width=10)
        entry.grid(row=row, column=1, padx=5, pady=2)
        if persen is not None: entry.insert(0, str(persen))
        
        self.ingredients.append([combo, entry])

    def save_formula(self):
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Nama formula tidak boleh kosong."); return
        if new_name != self.formula_name and new_name in self.parent_app.formulas:
            messagebox.showerror("Error", "Nama formula sudah ada."); return
        
        new_composition = {}; total_persen = 0
        try:
            for combo, entry in self.ingredients:
                bahan = combo.get(); persen_str = entry.get().strip()
                if bahan and persen_str:
                    persen = float(persen_str)
                    new_composition[bahan] = persen; total_persen += persen
        except ValueError:
            messagebox.showerror("Error", "Persentase harus berupa angka."); return
        
        if abs(total_persen - 100.0) > 0.1:
            if not messagebox.askyesno("Peringatan", f"Total persentase adalah {total_persen:.2f}%, bukan 100%.\nTetap simpan?"):
                return
        
        if self.formula_name and new_name != self.formula_name:
            del self.parent_app.formulas[self.formula_name]
        
        self.parent_app.formulas[new_name] = new_composition
        self.parent_app.save_formulas()
        self.refresh_callback()
        self.parent_app.refresh_formula_combos()
        self.destroy()

# --- [BARU] KELAS UNTUK MANAJER & EDITOR BAHAN BAKU ---

class BahanBakuManagerWindow(tk.Toplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.title("Manajer Bahan Baku")
        self.geometry("600x400")
        self.transient(parent_app)
        self.grab_set()

        list_frame = ttk.Frame(self, padding=10); list_frame.pack(fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame); self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.refresh_listbox()

        btn_frame = ttk.Frame(self, padding=10); btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Tambah Baru", command=self.add_bahan).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Edit Pilihan", command=self.edit_bahan).pack(side=tk.LEFT, expand=True, padx=5)
        ttk.Button(btn_frame, text="Hapus Pilihan", command=self.delete_bahan).pack(side=tk.LEFT, expand=True, padx=5)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for name in sorted(self.parent_app.bahan_baku.keys()):
            self.listbox.insert(tk.END, name)

    def add_bahan(self):
        BahanBakuEditorWindow(self, None, self.refresh_listbox)

    def edit_bahan(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        BahanBakuEditorWindow(self, self.listbox.get(selected_indices[0]), self.refresh_listbox)

    def delete_bahan(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices: return
        name = self.listbox.get(selected_indices[0])
        if messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus bahan baku '{name}'? Ini juga akan menghapusnya dari formula yang ada."):
            del self.parent_app.bahan_baku[name]
            # Hapus bahan ini dari semua formula yang ada
            for formula in self.parent_app.formulas.values():
                formula.pop(name, None)
            
            self.parent_app.save_bahan_baku()
            self.parent_app.save_formulas()
            self.refresh_listbox()
            self.parent_app.refresh_ui_panels()

class BahanBakuEditorWindow(tk.Toplevel):
    def __init__(self, parent_manager, bahan_name, refresh_callback):
        super().__init__(parent_manager)
        self.parent_manager = parent_manager
        self.parent_app = parent_manager.parent_app
        self.bahan_name = bahan_name
        self.refresh_callback = refresh_callback
        self.title(f"Editor Bahan Baku: {bahan_name or 'Baru'}")
        self.transient(parent_manager); self.grab_set()

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Nama Bahan:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        if bahan_name: self.name_entry.insert(0, bahan_name)

        self.nutrisi_entries = {}
        nutrisi_keys = ['harga', 'pk', 'em', 'ca', 'p', 'sk']
        for i, key in enumerate(nutrisi_keys, 1):
            ttk.Label(main_frame, text=f"{key.upper()}:").grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry = ttk.Entry(main_frame, width=15)
            entry.grid(row=i, column=1, padx=5, pady=5)
            if bahan_name:
                entry.insert(0, str(self.parent_app.bahan_baku[bahan_name].get(key, 0.0)))
            self.nutrisi_entries[key] = entry
            
        ttk.Button(main_frame, text="Simpan", command=self.save_bahan).grid(row=len(nutrisi_keys)+1, column=0, columnspan=2, pady=10)

    def save_bahan(self):
        new_name = self.name_entry.get().strip()
        if not new_name: messagebox.showerror("Error", "Nama bahan tidak boleh kosong."); return
        if new_name != self.bahan_name and new_name in self.parent_app.bahan_baku:
            messagebox.showerror("Error", "Nama bahan sudah ada."); return
        
        new_data = {}
        try:
            for key, entry in self.nutrisi_entries.items():
                new_data[key] = float(entry.get())
        except ValueError:
            messagebox.showerror("Error", "Semua nilai nutrisi harus berupa angka."); return

        # Ganti nama bahan di semua formula yang ada jika nama berubah
        if self.bahan_name and new_name != self.bahan_name:
            for formula_data in self.parent_app.formulas.values():
                if self.bahan_name in formula_data:
                    formula_data[new_name] = formula_data.pop(self.bahan_name)
            self.parent_app.save_formulas()
            del self.parent_app.bahan_baku[self.bahan_name]
        
        self.parent_app.bahan_baku[new_name] = new_data
        self.parent_app.save_bahan_baku()
        self.refresh_callback()
        self.parent_app.refresh_ui_panels()
        self.destroy()