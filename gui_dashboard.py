# gui_dashboard.py

import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config
import data_manager

class DashboardWindow(tk.Toplevel):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.title("Dasbor Analisis Biaya Pakan")
        self.geometry("900x700")
        self.transient(parent_app)
        self.grab_set()

        # Muat data log menggunakan Pandas
        logs = data_manager.load_json(config.LOG_FILE, default_data=[])
        if not logs:
            ttk.Label(self, text="Belum ada data di buku catatan.", font=("Helvetica", 14)).pack(pady=50)
            return
            
        self.df = pd.DataFrame(logs)
        self.df['tanggal'] = pd.to_datetime(self.df['tanggal'])
        self.df['total_biaya'] = self.df['total_biaya'].astype(float)

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # KPI Frame
        kpi_frame = ttk.LabelFrame(main_frame, text="Indikator Kunci", padding=10)
        kpi_frame.pack(fill=tk.X, pady=5)
        
        total_biaya = self.df['total_biaya'].sum()
        rata_biaya_kg = total_biaya / self.df['jumlah_kg'].sum() if self.df['jumlah_kg'].sum() > 0 else 0

        ttk.Label(kpi_frame, text=f"Total Biaya Pakan: Rp {total_biaya:,.2f}", font=("Helvetica", 12, "bold")).pack(anchor='w')
        ttk.Label(kpi_frame, text=f"Biaya Rata-rata per Kg: Rp {rata_biaya_kg:,.2f}", font=("Helvetica", 12, "bold")).pack(anchor='w')

        # Chart Frame
        chart_frame = ttk.LabelFrame(main_frame, text="Grafik Analisis", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.create_pie_chart(chart_frame)

    def create_pie_chart(self, parent):
        # Agregasi data: Hitung total biaya per bahan baku
        bahan_costs = {}
        for _, row in self.df.iterrows():
            for bahan, data in row['rincian_bahan'].items():
                if bahan not in bahan_costs:
                    bahan_costs[bahan] = 0
                bahan_costs[bahan] += data['biaya']
        
        # Siapkan data untuk pie chart
        labels = list(bahan_costs.keys())
        sizes = list(bahan_costs.values())
        
        if not labels: return # Jangan buat chart jika tidak ada data

        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
        ax.axis('equal') # Pastikan pie chart berbentuk lingkaran
        ax.set_title("Komposisi Biaya per Bahan Baku", fontsize=12, fontweight='bold')
        
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)