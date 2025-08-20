from io import BytesIO
from typing import Optional

from gtts import gTTS


def synthesize_ru_speech_to_bytes(text: str, slow: bool = False) -> Optional[bytes]:
    try:
        tts = gTTS(text=text, lang="ru", slow=slow)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return None
