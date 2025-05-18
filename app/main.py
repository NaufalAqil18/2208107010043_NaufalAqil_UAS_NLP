from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os

from .stt import transcribe_speech_to_text
from .llm import generate_response
from .tts import transcribe_text_to_speech

app = FastAPI()

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/wave"]:
        raise HTTPException(status_code=400, detail="File harus berformat WAV")

    try:
        # baca seluruh isi file audio upload sebagai bytes
        file_bytes = await file.read()

        # panggil fungsi STT dengan bytes audio
        text = transcribe_speech_to_text(file_bytes)
        print(text)
        if not text or text.startswith("[ERROR]"):
            raise HTTPException(status_code=400, detail="Gagal mengenali suara")

        # generate response LLM
        response_text = generate_response(text)

        # panggil fungsi TTS dengan teks response dan path output
        path_hasil= transcribe_text_to_speech(response_text)

        # kembalikan file audio output ke client
        return FileResponse(path_hasil, media_type="audio/wav", filename="tts_response.wav")

    except Exception as e:
        import traceback
        print("Error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan server: {str(e)}")
