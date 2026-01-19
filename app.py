import streamlit as st
import pandas as pd
import requests
import json
import os

# --- KONFIGURASI ---
# API Key Google Gemini 
API_KEY = "AIzaSyCZyBx4Z10PDTAZ6TCGmf5TzLKBGB_uMnk"

st.set_page_config(page_title="AI Data Analyst (REST API)", layout="wide")
st.title("🤖 Asisten Analisis Data")
st.markdown("---")

# --- 1. FUNGSI LOGIKA (BACKEND) ---

def hitung_fakta_data(df):
    """
    Python yang menghitung (pasti akurat), hasilnya jadi teks buat contekan AI.
    """
    summary = "Hasil perhitungan berdasarkan dataset:\n"
    
   # Deteksi Nama Kolom (Biar fleksibel)
    col_omzet = 'Total_Penjualan' if 'Total_Penjualan' in df.columns else None
    col_unit = 'Unit_Terjual' if 'Unit_Terjual' in df.columns else None
    
    # 1. Total Global
    if col_omzet:
        summary += f"- Total Omzet Global: Rp {df[col_omzet].sum():,.0f}\n"
    if col_unit:
        summary += f"- Total Unit Terjual Global: {df[col_unit].sum()} unit\n"
    
    # 2. Rincian per Kategori (Wilayah, Produk, dll)
    # Ambil semua kolom teks
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    for col in cat_cols:
        # --- PERBAIKAN: SKIP KOLOM TANGGAL ---
        # Agar output tidak kepanjangan gara-gara list tanggal
        if 'tanggal' in col.lower() or 'date' in col.lower():
            continue 
            
        summary += f"\n[Kategori: {col}]\n"
        
        # A. Rincian Omzet (Uang)
        if col_omzet:
            group_omzet = df.groupby(col)[col_omzet].sum().sort_values(ascending=False)
            summary += "  > Rincian Omzet (Rp):\n"
            for idx, val in group_omzet.items():
                summary += f"    - {idx}: Rp {val:,.0f}\n"
        
        # B. Rincian Unit (Barang) -- FITUR BARU
        if col_unit:
            group_unit = df.groupby(col)[col_unit].sum().sort_values(ascending=False)
            summary += "  > Rincian Unit (Pcs):\n"
            for idx, val in group_unit.items():
                summary += f"    - {idx}: {val} pcs\n"
                
    return summary

# --- 2. FUNGSI AI (GEMINI) ---
def tanya_gemini(pertanyaan, history, data_context, api_key):
    # Model Gemini 2.5 Flash
    model_name = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # Susun History
    chat_history = ""
    for chat in history[-5:]: 
        role = "User" if chat["role"] == "user" else "Assistant"
        chat_history += f"{role}: {chat['content']}\n"

    # Prompt
    final_prompt = f"""
    Anda adalah Data Analyst.
    
    DATA FAKTA (CONTEKAN):
    {data_context}
    
    RIWAYAT CHAT:
    {chat_history}
    
    PERTANYAAN BARU: {pertanyaan}
    
    INSTRUKSI:
    1. Jawablah berdasarkan 'DATA FAKTA'.
    2. Jika ditanya jumlah UNIT, lihat bagian 'Rincian Unit'.
    3. Jika ditanya OMZET/PENJUALAN, lihat bagian 'Rincian Omzet'.
    4. WAJIB sertakan perhitungan sederhana dalam kurung.
       Contoh: "Total Unit Bali adalah 150 pcs. (Rincian: Mouse 50 + Laptop 100)"
    """
    
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error API: {response.text}"
    except Exception as e:
        return f"Gagal koneksi: {e}"

# --- 2. USER INTERFACE (STREAMLIT) ---

# Sidebar: Upload & Reset
with st.sidebar:
    st.header("🗂️ Analisis Data")
    uploaded_file = st.file_uploader("Upload CSV Laporan", type=["csv"])
    
    st.markdown("---")
    if st.button("🗑️ Hapus Chat & Mulai Baru", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Area
if uploaded_file:
    # A. Load Data
    df = pd.read_csv(uploaded_file)
    
    # B. TAMPILKAN DATAFRAME (REQUEST ANDA)
    st.subheader("📊 Preview Data (5 Baris Teratas)")
    st.dataframe(df.head()) # Menampilkan tabel
    st.markdown("---")

    # C. Hitung Fakta (Sekali saja)
    if "context_data" not in st.session_state:
        st.session_state.context_data = hitung_fakta_data(df)

    # D. Inisialisasi Chat
    st.header("💬 Diskusi Data")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # E. Render Chat Lama
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # F. Input Chat Baru
    if user_input := st.chat_input("Tanya tentang total, wilayah, atau produk..."):
        # 1. Tampilkan User
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Proses AI
        with st.chat_message("assistant"):
            with st.spinner("Sedang menganalisis & menghitung..."):
                jawaban = tanya_gemini(
                    user_input, 
                    st.session_state.messages, 
                    st.session_state.context_data, 
                    API_KEY
                )
                st.markdown(jawaban)
                
                # Opsional: Tampilkan contekan hitungan di bawah jawaban
                with st.expander("🔍 Lihat Data Mentah (Debugging)"):
                    st.text(st.session_state.context_data)
        
        # 3. Simpan
        st.session_state.messages.append({"role": "assistant", "content": jawaban})

else:
    st.info("👋 Silakan upload file CSV di sidebar untuk memulai.")