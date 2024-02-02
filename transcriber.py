import time
import os
from datetime import datetime
import ffmpeg
from faster_whisper import WhisperModel
from tqdm import tqdm
import pysrt
import math

from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor
from configparser import ConfigParser

def translate(text, source, target):
    translator = GoogleTranslator() # YOU MUST CREATE ONE FOR EACH REQUEST OR THE MULTI-THREADING WILL FAIL, SINCE EACH INSTANCE HANDLE ONE REQUEST AT a TIME.
    translator.source = source
    translator.target = target
    return translator.translate(text)

def translate_captions(captions, batch_size, source_lang, target_lang, num_workers):
    try:
        if not source_lang or not target_lang:
            raise ValueError("Please select both source and target languages")

        sentences = [text for start, end, text in captions]

        n = len(sentences)
        n_batches = math.ceil(n / int(batch_size))

        # Multi-Threading
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(
                    lambda batch_id: translate(batch_id, source_lang, target_lang),
                    "\n".join(sentences[batch_id * int(batch_size): (batch_id + 1) * int(batch_size)])
                ) for batch_id in range(n_batches)
            ]

        translated_text = ("\n".join([future.result() for future in futures])).split("\n")
        new_captions = [(start, end, translated) for (start, end, text), translated in zip(captions, translated_text)]
        return new_captions
        
    except Exception as e:
        print(f"Error: {e}")


def transcribe_audio(audio):
    segments, info = model.transcribe(audio, vad_filter=True)
    captions = []
    for segment in tqdm(segments, desc="Transcribing"):
        captions.append((segment.start, segment.end, segment.text))
    return captions

def get_info(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), {})
        audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), {})
        return video_info, audio_info
    except Exception as e:
        print(f"Error probing file: {e}")
        return {}, {}

def extract_and_save_audio(input_video, output_audio, start_time=None, end_time=None):
    input_args = {}
    if start_time is not None:
        input_args['ss'] = start_time
    if end_time is not None:
        input_args['to'] = end_time
    
    try:
        ffmpeg.input(input_video, **input_args).output(output_audio).run(overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        print(f"Error: {e.stderr}")
        raise




# Main function
def main():
    last_transcribed_end = 0  # Initialize with 0 seconds
    last_index = 1  # Initialize with 1 if SRT file doesn't exist or has no captions
    if os.path.exists(CAPTION_FILE):
        subtitles = pysrt.open(CAPTION_FILE)
        if subtitles:
            last_transcribed_end = subtitles[-1].end.ordinal / 1000.0
            last_index = subtitles[-1].index

    print("--- Starting --- ")
    while True:
        # Get current video info
        video_info, _ = get_info(INPUT_VIDEO)
        duration = float(video_info.get('duration', 0))
        
        # Check if video length is sufficient
        if duration < (last_transcribed_end + T_DELAY):
            print("wait")
            time.sleep(WAIT_TIME)  # Wait and check again
            continue
        print("--- passed --- ")

        # Extract audio
        start_time = last_transcribed_end
        end_time = duration
        last_transcribed_end = end_time
        temp_audio = "temp_audio.mp3"
        extract_and_save_audio(INPUT_VIDEO, temp_audio, start_time, end_time)
        
        # Transcribe audio
        print("-- Transcribing --")
        captions = transcribe_audio(temp_audio)

        # Translate captions
        if TRANSLATE:
            print("-- Translating --")
            captions = translate_captions(
                captions=captions, 
                batch_size=BATCH_SIZE,
                source_lang=SOURCE_LANG,
                target_lang=TARGET_LANG,
                num_workers=NUM_WORKERS
                )   
        
        print("--- Saving ---")
        # Adjust captions timing
        adjusted_captions = [(start_time + start, start_time + end, text) for start, end, text in captions]
        
        # Save or append captions to SRT file
        with open(CAPTION_FILE, 'a', encoding='utf-8') as f:
            for idx, (start, end, text) in enumerate(adjusted_captions, start=last_index):
                start_time = datetime.utcfromtimestamp(start)
                end_time = datetime.utcfromtimestamp(end)
                f.write(f"{idx}\n{start_time.strftime('%H:%M:%S,%f')[:-3]} --> {end_time.strftime('%H:%M:%S,%f')[:-3]}\n{text}\n\n")
            last_index = idx +1 # Update last index for next iteration

        
if __name__ == "__main__":
    # Load config from file
    config = ConfigParser()
    config.read('transcriber.ini')
    # Constants
    T_DELAY = config.getint('Constants', 'T_DELAY')
    WAIT_TIME = config.getint('Constants', 'WAIT_TIME')
    # Translation
    TRANSLATE = config.getboolean('Translation', 'TRANSLATE')
    BATCH_SIZE = config.getint('Translation', 'BATCH_SIZE')
    SOURCE_LANG = config.get('Translation', 'SOURCE_LANG')
    TARGET_LANG = config.get('Translation', 'TARGET_LANG')
    NUM_WORKERS = config.getint('Translation', 'NUM_WORKERS')
    # Video and captions
    INPUT_VIDEO = config.get('Video', 'INPUT_VIDEO')
    CAPTION_FILE = config.get('Video', 'CAPTION_FILE')
    # Load model
    MODEL = config.get('Model', 'MODEL')
    DEVICE = config.get('Model', 'DEVICE')
    COMPUTE_TYPE = config.get('Model', 'COMPUTE_TYPE')

    print(f"-- Loading Model: {MODEL} --")
    model = WhisperModel(MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)
    # Run video player
    print(f"-- Running the process on {INPUT_VIDEO} and saving into {CAPTION_FILE} --")
    main()
