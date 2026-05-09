import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import wave

# Konfigurasi Halaman
st.set_page_config(page_title="Affiliate Labs Ultra", layout="wide", page_icon="🎙️")

st.title("🎙️ Affiliate Labs")
st.write("Kontrol Penuh: Generate Script -> Review -> Generate Voice")

# API Key Bos
API_KEY = API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=API_KEY)

# --- State Management ---
# Biar script yang sudah digenerate tidak hilang saat kita klik tombol lain
if 'generated_script' not in st.session_state:
    st.session_state.generated_script = ""

# --- Sidebar Pengaturan ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    # Pilihan suara premium sesuai gambar Bos
    voice_choice = st.selectbox("Pilih Voice Profile:", 
                                ["Aoede", "Puck", "Charon", "Kore", "Fenrir", "Autonoe"])
    
    st.subheader("Director's Note")
    style_choice = st.selectbox("Style Suara:", ["Promo/Hype", "Natural", "Friendly", "Semangat"])
    pace_choice = st.selectbox("Pace (Kecepatan):", ["Natural", "Fast", "Slow"])
    
    st.markdown("---")
    voice_hint = st.text_area("Hint Karakter Suara (Opsional):", 
                              placeholder="Contoh: Suara pria dewasa yang berwibawa...")

# --- Layout Utama ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 1. Input Produk")
    uploaded_file = st.file_uploader("Upload Foto Produk...", type=["jpg", "png", "jpeg"])
    
    # Input Hint Tambahan untuk Produk
    product_hint = st.text_input("Hint Produk (Opsional):", 
                                 placeholder="Contoh: Ini meja lipat kayu jati tahan air...")
    
    target_duration = st.slider("Target Durasi Script (detik):", 15, 60, 30)

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        
        if st.button("Langkah 1: Generate Script"):
            with st.spinner('Gemini lagi menganalisa gambar...'):
                try:
                    # Logic Prompt Script
                    hint_text = f"Berikut adalah info tambahan: {product_hint}." if product_hint else ""
                    prompt = f"""
                    Tolong buatkan script promo affiliate TikTok untuk produk di gambar ini.
                    {hint_text}
                    Target durasi: {target_duration} detik.
                    Berikan output HANYA teks dialognya saja, tanpa keterangan visual.
                    """
                    
                    txt_response = client.models.generate_content(
                        model="gemini-3.1-flash-lite", #
                        contents=[prompt, image]
                    )
                    st.session_state.generated_script = txt_response.text
                except Exception as e:
                    st.error(f"Gagal generate script: {e}")

with col2:
    st.subheader("📝 2. Review & Generate Voice")
    
    # Kolom teks untuk review script (Bos bisa edit manual di sini!)
    final_script = st.text_area("Edit Script di Sini:", 
                                value=st.session_state.generated_script, 
                                height=250)

    if final_script:
        if st.button("Langkah 2: Generate Premium Voice"):
            with st.spinner('Meracik suara premium...'):
                try:
                    # Model TTS Preview
                    tts_model = "gemini-3.1-flash-tts-preview"
                    
                    # Gabungkan hint suara jika ada
                    v_hint = f"Karakter Pembicara: {voice_hint}." if voice_hint else ""
                    full_voice_prompt = f"Style: {style_choice}, Pace: {pace_choice}. {v_hint} Bacakan teks berikut: {final_script}"
                    
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

                    # Ambil data audio mentah
                    audio_parts = [p for p in speech_response.candidates[0].content.parts if p.inline_data]
                    
                    if audio_parts:
                        raw_bytes = audio_parts[0].inline_data.data
                        
                        # Fix Header Manual
                        fixed_audio = io.BytesIO()
                        with wave.open(fixed_audio, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(24000)
                            wav_file.writeframes(raw_bytes)
                        
                        final_data = fixed_audio.getvalue()
                        st.audio(final_data, format="audio/wav")
                        st.success(f"Suara {voice_choice} siap digunakan!")
                    else:
                        st.warning("Data audio tidak ditemukan.")
                except Exception as e:
                    st.error(f"Gagal generate audio: {e}")
    else:
        st.write("Silakan generate atau tulis script dulu di Langkah 1.")

st.divider()
st.caption("Affiliate Labs Ultra | Dibuat oleh Akmal 🚀")