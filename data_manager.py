# data_manager.py

import json
import os
from datetime import datetime
from fpdf import FPDF
from tkinter import messagebox
import config

def load_json(filepath, default_data=None):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        if default_data is not None:
            save_json(filepath, default_data)
        return default_data if default_data is not None else {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        messagebox.showerror("Error Memuat File", f"Gagal memuat {filepath}.\nError: {e}\nMenggunakan data default.")
        return default_data if default_data is not None else {}

def save_json(filepath, data):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except IOError as e:
        messagebox.showerror("Error Menyimpan File", f"Gagal menyimpan ke {filepath}.\nError: {e}")
        return False

def print_to_pdf(filepath, report_text):
    try:
        pdf = FPDF()
        pdf.add_page()
        if os.path.exists(config.LOGO_FILE):
            pdf.image(config.LOGO_FILE, x=10, y=8, w=15)
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Laporan Analisis Pakan - Pa-Ri Pertanian Mandiri", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "Disusun oleh: Pari", ln=True, align='C')
        
        creation_date = datetime.now().strftime("%d %B %Y, %H:%M:%S WIB")
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 10, f"Tanggal Cetak: {creation_date}", ln=True, align='R')
        pdf.ln(5)
        
        pdf.set_font("Courier", '', 9)
        pdf.multi_cell(0, 5, report_text)
        
        pdf.output(filepath)
        messagebox.showinfo("Sukses", f"Laporan PDF berhasil disimpan di:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuat file PDF:\n{e}")

# BARU: Fungsi untuk menambahkan catatan ke file log
def append_to_log(log_entry):
    """
    Membaca file log (sebuah list), menambahkan entri baru, lalu menyimpannya kembali.
    """
    try:
        logs = load_json(config.LOG_FILE, default_data=[])
        logs.append(log_entry)
        save_json(config.LOG_FILE, logs)
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan catatan ke log:\n{e}")