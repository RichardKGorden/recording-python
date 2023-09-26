import asyncio
import pyaudio
import wave
from playwright.async_api import async_playwright

# Function to capture HTML content using Playwright and record audio simultaneously
async def capture_html_content_and_audio(playwright, audio_output_file):
    try:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(record_video_dir="videos/", viewport={"width": 1920, "height": 1080}, record_video_size={"width": 1920, "height": 1080})
        page = await context.new_page()

        file_path = "E:\\recording_initial\\recording\\hello.html"
        await page.goto(f"file://{file_path}")

        # Initialize PyAudio for audio recording
        audio = pyaudio.PyAudio()

        # Define audio recording settings
        format = pyaudio.paInt16
        channels = 2
        sample_rate = 44100
        chunk = 1024

        # Open an audio stream for recording
        audio_stream = audio.open(format=format, channels=channels,
                                rate=sample_rate, input=True,
                                frames_per_buffer=chunk)

        # Create a WAV file to save the audio
        audio_wavefile = wave.open(audio_output_file, 'wb')
        audio_wavefile.setnchannels(channels)
        audio_wavefile.setsampwidth(audio.get_sample_size(format))
        audio_wavefile.setframerate(sample_rate)

        # Record audio and capture video simultaneously
        print("Recording audio and capturing video for 5 seconds...")
        audio_frames = []

        # Start recording audio in a separate thread
        async def record_audio():
            while True:
                audio_data = audio_stream.read(chunk)
                audio_frames.append(audio_data)
                audio_wavefile.writeframes(audio_data)

        audio_task = asyncio.create_task(record_audio())
        
        # Record video
        # Add code here to capture HTML content (e.g., take a screenshot or record video)
        # Make sure to record video frames continuously

        # Record for 5 seconds
        await asyncio.sleep(5)
        print("Recording audio and capturing video for 5 seconds...")
        # Stop recording audio
        audio_task.cancel()

        # Close audio stream and file
        audio_stream.stop_stream()
        audio_stream.close()
        audio_wavefile.close()
        audio.terminate()

        # Close the video recording context
        await context.close()
        await browser.close()

        print("Audio and video recording completed after 5 seconds.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

async def main():
    async with async_playwright() as playwright:
        audio_output_file = "output_audio.wav"
        await capture_html_content_and_audio(playwright, audio_output_file)

# Run the main function
asyncio.run(main())
