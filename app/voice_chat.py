
import threading
import numpy as np
import sounddevice as sd
import whisper
import time
import logging
import soundfile as sf
import pyttsx3

WHISPER_MODEL_NAME = "base"
SAMPLE_RATE = 16000
USER_ID_FOR_GRAPH = "local_voice_test_user"
AGE_GROUP_FOR_GRAPH = "Young Adults (19-30)"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

whisper_model = None
try:
    logger.info(f"Loading Whisper model: {WHISPER_MODEL_NAME}...")
    whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device='cpu')
    logger.info("Whisper model loaded successfully.")
except Exception as e:
    logger.error(f"Fatal: Error loading Whisper model: {e}", exc_info=True)
    exit()

try:
    from app.chat_graph import graph as langchain_graph
    logger.info("LangChain graph imported successfully.")
except ImportError:
    logger.error("Fatal: Could not import LangChain graph from 'app.chat_graph'. Ensure path is correct.")
    exit()
except Exception as e:
    logger.error(f"Fatal: Error importing/initializing LangChain graph: {e}", exc_info=True)
    exit()


def record_audio_sync():
    audio_data = []
    stop_event = threading.Event()

    def record_stream():
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=callback):
            logger.info("--- Recording: Speak now! Press Enter to stop. ---")
            stop_event.wait()
            logger.info("--- Recording stopped. ---")

    def callback(indata, frames, time, status):
        if status:
            logger.warning(f"Sounddevice status: {status}")
        audio_data.append(indata.copy())

    def wait_for_enter():
        input()
        stop_event.set()

    stopper_thread = threading.Thread(target=wait_for_enter)
    stopper_thread.start()
    record_stream()
    stopper_thread.join()

    if not audio_data:
        logger.warning("No audio data recorded.")
        return None

    full_audio = np.concatenate(audio_data, axis=0)
    return full_audio

def transcribe_audio_sync(audio_np: np.ndarray) -> str | None:
    if whisper_model is None:
        logger.error("Cannot transcribe, Whisper model not loaded.")
        return None
    if audio_np is None or audio_np.size == 0:
        logger.error("Cannot transcribe, audio data is missing or empty.")
        return None

    try:
        temp_filename = "temp_recorded_audio.wav"
        logger.info(f"Saving recorded audio to {temp_filename} for inspection...")
        sf.write(temp_filename, audio_np, SAMPLE_RATE)
        logger.info("Temporary audio file saved.")
    except Exception as write_err:
        logger.error(f"Could not save temporary audio file: {write_err}", exc_info=True)
    

    logger.info(f"Transcribing {len(audio_np)/SAMPLE_RATE:.2f} seconds of audio...")
    try:
        logger.info(f"Audio data before transcription - Shape: {audio_np.shape}, Dtype: {audio_np.dtype}, Min: {np.min(audio_np):.4f}, Max: {np.max(audio_np):.4f}, Contains NaN: {np.isnan(audio_np).any()}, Contains Inf: {np.isinf(audio_np).any()}")
        if audio_np.ndim == 2 and audio_np.shape[1] == 1:
             logger.info("Audio is 2D with one channel, flattening to 1D for Whisper.")
             audio_np = audio_np.flatten()
        elif audio_np.ndim > 1:
             logger.warning(f"Audio data has unexpected dimensions ({audio_np.shape}) before transcription!")

        result = whisper_model.transcribe(audio_np, fp16=False)
        transcribed_text = result["text"].strip()
        logger.info(f"Transcription result: '{transcribed_text}'")
        return transcribed_text

    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        return None

def run_langchain_sync(thread_id: str, age_group: str, user_input_text: str) -> str | None:
    global langchain_graph

    if not user_input_text:
        logger.warning("Skipping LangChain graph: No input text.")
        return None

    config = {"configurable": {"thread_id": thread_id}}
    state = {
        "messages": [user_input_text],
        "age_group": age_group
    }

    try:
        logger.info(f"Streaming Langchain graph for thread {thread_id}...")
        start_time = time.time()

        for event in langchain_graph.stream(state, config):
            for val in event.values():
                state = val
                agent_message = state["messages"][-1]
            agent_message = str(agent_message)

        end_time = time.time()
        logger.info(f"Langchain graph streaming took {end_time - start_time:.2f} seconds.")


        return agent_message

    except Exception as e:
        logger.error(f"Langchain graph processing failed during stream for thread {thread_id}: {e}", exc_info=True)
        return None



def speak_text_sync(text: str):
    if not text:
        logger.warning("TTS skipped: No text provided.")
        return
    try:
        engine = pyttsx3.init()

        logger.info(f"Attempting to speak: '{text[:60]}...'")
        engine.say(text)
        engine.runAndWait() 
        engine.stop() 
        logger.info("TTS playback finished.")
    except Exception as e:
        logger.error(f"pyttsx3 TTS failed: {e}", exc_info=True)
        print("\n[TTS Error - Could not speak response. Check logs.]\n")
if __name__ == "__main__":
    logger.info("Starting local voice interaction script...")
    thread_id = "hasin"
    logger.info(f"Using Thread ID: {thread_id}")

    audio_data_np = record_audio_sync()

    transcribed_text = None
    if audio_data_np is not None and audio_data_np.size > 0:
        transcribed_text = transcribe_audio_sync(audio_data_np)
    else:
        logger.info("Skipping transcription because no audio was recorded.")

    agent_reply = None
    if transcribed_text:
        agent_reply = run_langchain_sync(thread_id, AGE_GROUP_FOR_GRAPH, transcribed_text)
    else:
        logger.info("Skipping LangChain graph because transcription failed or produced no text.")

    if agent_reply:
        print("\n" + "="*20 + " Agent Response " + "="*20)
        print(agent_reply)
        print("="*56)
        speak_text_sync(agent_reply)
    else:
        logger.warning("No final agent response generated.")

    logger.info("--- Script finished ---")