import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Nama database baru sesuai spesifikasi
DB_NAME = 'prediksi_diabetes.db'

def run_query(sql, params=()):
    """Fungsi helper untuk mengeksekusi query database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    try:
        with conn:
            return conn.execute(sql, params).fetchall()
    finally:
        conn.close()

def init_db():
    """Inisialisasi tabel pasien jika belum ada."""
    run_query('''CREATE TABLE IF NOT EXISTS pasien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_pasien TEXT NOT NULL,
        usia INTEGER NOT NULL,
        gula_darah REAL NOT NULL,
        bmi REAL NOT NULL,
        riwayat_ortu TEXT NOT NULL,
        hasil_prediksi TEXT NOT NULL
    )''')

def add_pasien(nama, usia, gula_darah, bmi, riwayat, hasil):
    """Menambahkan record data pasien baru ke database."""
    run_query('''INSERT INTO pasien 
                 (nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (nama, usia, gula_darah, bmi, riwayat, hasil))

def get_pasien():
    """Mengambil seluruh data pasien dari database."""
    return run_query('''SELECT id, nama_pasien, usia, gula_darah, bmi, riwayat_ortu, hasil_prediksi 
                        FROM pasien ORDER BY id DESC''')

def update_pasien(pid, nama, usia, gula_darah, bmi, riwayat, hasil):
    """Memperbarui data pasien berdasarkan ID."""
    run_query('''UPDATE pasien SET 
                 nama_pasien = ?, usia = ?, gula_darah = ?, bmi = ?, riwayat_ortu = ?, hasil_prediksi = ? 
                 WHERE id = ?''', 
              (nama, usia, gula_darah, bmi, riwayat, hasil, pid))

def delete_pasien(pid):
    """Menghapus data pasien dari database."""
    run_query('DELETE FROM pasien WHERE id = ?', (pid,))

def hitung_prediksi_risiko(gula_darah, bmi, riwayat_ortu):
    """
    Menentukan tingkat risiko diabetes berdasarkan kondisi acuan kesehatan:
    - Gula Darah >= 200: Tinggi / Sangat Tinggi
    - Gula Darah 140-199: Sedang / Tinggi (tergantung BMI & riwayat)
    - Gula Darah < 140:
      - BMI >= 30: Waspada / Sedang
      - BMI < 30 & Ada Riwayat: Waspada
      - BMI < 30 & Tanpa Riwayat: Rendah
    """
    has_history = (riwayat_ortu.strip().capitalize() == 'Ya')

    if gula_darah >= 200:
        if bmi >= 30 or has_history:
            return "Sangat Tinggi", "#B71C1C"  # Merah Tua
        return "Tinggi", "#D32F2F"              # Merah

    elif 140 <= gula_darah <= 199:
        if bmi >= 30 or has_history:
            return "Tinggi", "#D32F2F"          # Merah
        return "Sedang", "#E65100"              # Oranye Tua

    else:  # gula_darah < 140
        if bmi >= 30:
            if has_history:
                return "Sedang", "#E65100"      # Oranye Tua
            return "Waspada", "#F57F17"         # Kuning/Oranye
        else:
            if has_history:
                return "Waspada", "#F57F17"     # Kuning/Oranye
            return "Rendah", "#2E7D32"          # Hijau

# Inisialisasi Database & Root Window
init_db()
selected_id = None

root = tk.Tk()
root.title("Aplikasi Prediksi Risiko Diabetes")
root.geometry("620x650")
root.resizable(False, False)

# Form Input Layout
frame_input = tk.LabelFrame(root, text=" Form Data Pasien ", padx=10, pady=10)
frame_input.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

tk.Label(frame_input, text="Nama Pasien:").grid(row=0, column=0, sticky="w", pady=4)
entry_nama = tk.Entry(frame_input, width=35)
entry_nama.grid(row=0, column=1, pady=4)

tk.Label(frame_input, text="Usia (Tahun):").grid(row=1, column=0, sticky="w", pady=4)
entry_usia = tk.Entry(frame_input, width=35)
entry_usia.grid(row=1, column=1, pady=4)

tk.Label(frame_input, text="Gula Darah (mg/dL):").grid(row=2, column=0, sticky="w", pady=4)
entry_gula = tk.Entry(frame_input, width=35)
entry_gula.grid(row=2, column=1, pady=4)

tk.Label(frame_input, text="Indeks Massa Tubuh (BMI):").grid(row=3, column=0, sticky="w", pady=4)
entry_bmi = tk.Entry(frame_input, width=35)
entry_bmi.grid(row=3, column=1, pady=4)

tk.Label(frame_input, text="Riwayat Diabetes Ortu:").grid(row=4, column=0, sticky="w", pady=4)
combo_riwayat = ttk.Combobox(frame_input, values=['Ya', 'Tidak'], state='readonly', width=33)
combo_riwayat.set('Tidak')
combo_riwayat.grid(row=4, column=1, pady=4)

# Label Tampilan Hasil Prediksi
label_hasil = tk.Label(
    root, 
    text="Hasil Prediksi: -", 
    font=('Helvetica', 11, 'bold'), 
    fg="black", 
    bg="#E0E0E0", 
    pady=8
)
label_hasil.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

def read_form():
    """Validasi dan pengambilan nilai dari elemen form."""
    nama = entry_nama.get().strip()
    usia_str = entry_usia.get().strip()
    gula_str = entry_gula.get().strip()
    bmi_str = entry_bmi.get().strip()
    riwayat = combo_riwayat.get()

    if not nama or not usia_str or not gula_str or not bmi_str:
        messagebox.showwarning("Peringatan", "Seluruh field data pasien wajib diisi.")
        return None

    try:
        usia = int(usia_str)
        if usia <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Validasi Gagal", "Usia harus berupa angka bulat positif.")
        return None

    try:
        gula = float(gula_str)
        bmi = float(bmi_str)
        if gula <= 0 or bmi <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Validasi Gagal", "Kadar Gula Darah dan BMI harus berupa angka desimal/posisi positif.")
        return None

    return nama, usia, gula, bmi, riwayat

def on_predict_and_add():
    """Memproses prediksi risiko dan menyimpan ke database."""
    data = read_form()
    if data:
        nama, usia, gula, bmi, riwayat = data
        kategori_risiko, warna_hex = hitung_prediksi_risiko(gula