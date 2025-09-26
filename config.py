# config.py

# --- TEMA WARNA ---
BG_COLOR = "#F5F5DC"
TEXT_COLOR = "#3D403D"
ACCENT_COLOR = "#6B8E23"
INPUT_BG = "#FFFFF0"

# --- NAMA FILE ---
STOCK_FILE = "stok_gudang.json"
FORMULA_FILE = "formulas.json"
BAHAN_BAKU_FILE = "bahan_baku.json" # BARU
LOGO_FILE = "logo.png"
LOG_FILE = "log_pakan.json" # BARU: Untuk buku catatan digital

# --- DATA DEFAULT (HANYA UNTUK PEMBUATAN FILE PERTAMA KALI) ---
BAHAN_BAKU_DEFAULT = {
    'Jagung Giling':   {"harga": 8000, "pk": 8.5,  "em": 3350, "ca": 0.02, "p": 0.25, "sk": 2.2},
    'Bungkil Kedelai': {"harga": 14000,"pk": 46.0, "em": 2450, "ca": 0.30, "p": 0.65, "sk": 6.0},
    'Tepung Ikan':     {"harga": 10500,"pk": 45.0, "em": 2800, "ca": 4.5,  "p": 2.5,  "sk": 1.0},
    'Dedak Bekatul':   {"harga": 6000, "pk": 13.0, "em": 2850, "ca": 0.1,  "p": 1.2,  "sk": 11.0},
    'Tepung Tulang':   {"harga": 4000, "pk": 0.0,  "em": 0,    "ca": 30.0, "p": 14.0, "sk": 0.0},
    'Minyak Kelapa':   {"harga": 17500,"pk": 0.0,  "em": 8600, "ca": 0.0,  "p": 0.0,  "sk": 0.0},
    'Premix':          {"harga": 25000,"pk": 0.0,  "em": 0,    "ca": 24.0, "p": 12.0, "sk": 0.0}
}
FORMULA_DEFAULT = {
    "Starter (Default)": { "Bungkil Kedelai": 50, "Tepung Ikan": 30, "Tepung Tulang": 10, "Minyak Kelapa": 8, "Premix": 2 },
    "Grower (Default)": { "Bungkil Kedelai": 45, "Tepung Ikan": 25, "Dedak Bekatul": 18, "Tepung Tulang": 10, "Premix": 2 },
    "Finisher (Default)": { "Bungkil Kedelai": 40, "Tepung Ikan": 20, "Dedak Bekatul": 28, "Tepung Tulang": 10, "Premix": 2 }
}
TARGET_NUTRISI_DEFAULT = { 'pk_min': 18.0, 'em_min': 2900, 'ca_min': 0.9, 'p_min': 0.45, 'sk_max': 5.0 }

# --- DATA ASUMSI & TARGET---
PROTEIN_IDEAL = {'Starter': 18.0, 'Grower': 16.0, 'Finisher': 14.0}
DISTRIBUSI_PAKAN = {'Starter': 0.20, 'Grower': 0.35, 'Finisher': 0.45}
RASIO_KONSENTRAT = {'Starter': 0.35, 'Grower': 0.30, 'Finisher': 0.25}
UMUR_FASE = {'Starter': 'Hari 1 - 30', 'Grower': 'Hari 31 - 60', 'Finisher': 'Hari 61 - Panen'}