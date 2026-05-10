import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import wave

# Konfigurasi Halaman
st.set_page_config(page_title="Affiliate Labs Ultra", layout="wide", page_icon="🎙️")

# CSS Custom biar tombolnya mencolok (Merah/Oranye sesuai tema affiliate)
# --- GANTI JADI INI ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #28a745; /* Warna Hijau Sukses */
        color: white;
        font-weight: bold;
        border: none;
        font-size: 18px;
    }
    .stButton>button:hover {
        background-color: #218838; /* Hijau lebih gelap pas kursor nempel */
        border: none;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Affiliate Labs")
st.write("Buat konten jualan makin mudah dan premium!")

# API Key Bos (Pake Secrets biar aman pas Online)
API_KEY = "AIzaSyAaVY13CRBgn18Uyhg4hVfJ0K2cmSlV_6Q"
client = genai.Client(api_key=API_KEY)

# --- State Management ---
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None

# --- BAGIAN PENGATURAN (Pindah dari Sidebar ke Utama) ---
st.info("🛠️ **Pengaturan Suara & Karakter**")
c1, c2, c3 = st.columns(3)
with c1:
    voice_choice = st.selectbox("Profil Vokal:", ["Aoede", "Puck", "Charon", "Kore", "Fenrir", "Autonoe"])
with c2:
    style_choice = st.selectbox("Gaya Bicara:", ["Promo/Hype", "Natural", "Friendly", "Semangat"])
with c3:
    pace_choice = st.selectbox("Kecepatan:", ["Natural", "Fast", "Slow"])

voice_hint = st.text_input("Hint Karakter (Opsional):", placeholder="Contoh: Suara ceria, suara ibu-ibu ramah...")

st.divider()

# --- Layout Utama ---
col_input, col_output = st.columns([1, 1])

with col_input:
    st.subheader("📸 1. Input Produk")
    uploaded_file = st.file_uploader("Upload Foto Produk...", type=["jpg", "png", "jpeg"])
    product_hint = st.text_input("Hint Produk:", placeholder="Contoh: Meja lipat kayu jati...")
    target_duration = st.slider("Target Durasi (detik):", 15, 60, 30)

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        # Tombol Langkah 1 (Dibuat Mencolok via CSS)
        if st.button("🔥 LANGKAH 1: BUAT SCRIPT"):
            with st.spinner('Gemini lagi menganalisa gambar...'):
                try:
                    hint_text = f"Info tambahan: {product_hint}." if product_hint else ""
                    prompt = f"""
BUATKAN SCRIPT PROMO TIKTOK BERDASARKAN GAMBAR.
INFO TAMBAHAN: {product_hint}
TARGET DURASI: {target_duration} detik.

PERATURAN KETAT:
1. HANYA hasilkan teks dialog yang akan dibacakan.
2. JANGAN pakai pembukaan seperti "Tentu," atau "Ini naskahnya".
3. JANGAN pakai tanda kurung, keterangan durasi (00:00), atau instruksi visual.
4. JANGAN pakai tanda bintang (**) atau simbol markdown lainnya.
5. LANGSUNG MULAI DARI KATA PERTAMA DIALOG.
"""
                    
                    txt_response = client.models.generate_content(
                        model="gemini-3.1-flash-lite",
                        contents=[prompt, image]
                    )
                    st.session_state.generated_script = txt_response.text
                    st.rerun() # Biar teksnya langsung muncul di sebelah
                except Exception as e:
                    st.error(f"Gagal: {e}")

with col_output:
    st.subheader("📝 2. Review & Suara")
    final_script = st.text_area("Edit Script Jika Perlu:", 
                                value=st.session_state.generated_script, 
                                height=200)

    if final_script:
        # Tombol Langkah 2 (Dibuat Mencolok via CSS)
        if st.button("🚀 LANGKAH 2: BUAT SUARA PREMIUM"):
            with st.spinner('Meracik suara premium...'):
                try:
                    tts_model = "gemini-3.1-flash-tts-preview"
                    v_hint = f"Karakter: {voice_hint}." if voice_hint else ""
                    full_voice_prompt = f"Style: {style_choice}, Pace: {pace_choice}. {v_hint} Teks: {final_script}"
                    
                    speech_response = client.models.generate_content(
                        model=tts_model,
                        contents=full_voice_prompt,
                        config=types.GenerateContentConfig(
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name=voice_choice.upper()
                                    )
                                )
                            )
                        )
                    )

                    audio_parts = [p for p in speech_response.candidates[0].content.parts if p.inline_data]
                    
                    if audio_parts:
                        raw_bytes = audio_parts[0].inline_data.data
                        fixed_audio = io.BytesIO()
                        with wave.open(fixed_audio, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(24000)
                            wav_file.writeframes(raw_bytes)
                        
                        st.session_state.audio_data = fixed_audio.getvalue()
                    else:
                        st.warning("Gagal mengambil data suara.")
                except Exception as e:
                    st.error(f"Gagal: {e}")

        # Tampilkan Audio Player dan Tombol Download jika audio sudah ada
        if st.session_state.audio_data:
            st.markdown("---")
            st.audio(st.session_state.audio_data, format="audio/wav")
            
            # Tombol Download Khusus (Warna Hijau biar beda)
            st.download_button(
                label="📥 DOWNLOAD VOICE OVER (Klik di sini)",
                data=st.session_state.audio_data,
                file_name=f"konten_umi_{voice_choice.lower()}.wav",
                mime="audio/wav",
                use_container_width=True
            )
            st.success("Suara berhasil dibuat! Klik tombol download di atas untuk menyimpan ke iPhone.")
    else:
        st.info("Script akan muncul di sini setelah Langkah 1 selesai.")

st.divider()
st.caption("Affiliate Labs Ultra | Dibuat Khusus untuk Umi & Bos Akmal 🚀")