import tempfile, gc
from pydub import AudioSegment

async def save_and_convert(audio):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(await audio.read())
        webm_path = tmp.name

    wav_path = webm_path.replace(".webm", ".wav")

    sound = AudioSegment.from_file(webm_path, format="webm")
    sound.export(wav_path, format="wav")
    sound = None
    gc.collect()

    return webm_path, wav_path
