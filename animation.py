import asyncio
import pyaudio
import wave
import subprocess
from playwright.async_api import async_playwright

# Function to capture HTML content using Playwright
async def capture_html_content(playwright):
    browser = await playwright.chromium.launch(headless=False,slow_mo=8000)
    context = await browser.new_context(record_video_dir="./", viewport={"width": 1920, "height": 1080}, record_video_size={"width": 1920, "height": 1080})
    page = await context.new_page()

    # Flag to track whether to start video recording
    start_recording = False

    async def handle_animation_finished():
        nonlocal start_recording
        print("Animation finished. Stopping recording.")
        await page.video.stop()  # Stop video recording when animation is finished
        start_recording = False

    file_path = "E:\\recording_initial\\recording\\hello.html"
    await page.goto(f"file://{file_path}")

    # Listen for a custom event indicating that the animation is finished
    await page.expose_binding('animationFinished', handle_animation_finished)

    # Add code here to capture HTML content (e.g., take a screenshot or record video)
    
    # Start video recording when the page is loaded
    video_file_name = "output-video.mp4"  # Adjust the video file name and format (e.g., "output-video.mp4")
    await page.video.start()
    start_recording = True

    # Wait for the animation to finish
    while start_recording:
        await asyncio.sleep(1)  # You can adjust the sleep duration

    await context.close()
    await browser.close()

# Function to record audio using PyAudio
def record_audio(audio_duration, audio_output_file):
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

    # Record audio
    print("Recording audio...")
    audio_frames = []
    for i in range(0, int(sample_rate / chunk * audio_duration)):
        audio_data = audio_stream.read(chunk)
        audio_frames.append(audio_data)
        audio_wavefile.writeframes(audio_data)

    # Close audio stream and file
    audio_stream.stop_stream()
    audio_stream.close()
    audio_wavefile.close()
    audio.terminate()

    print("Audio recording completed.")


async def main():
    async with async_playwright() as playwright:
        # Start capturing HTML content using Playwright in parallel
        capture_task = asyncio.create_task(capture_html_content(playwright))

        # Start recording audio using PyAudio in parallel
        audio_duration = 10  # Adjust the duration as needed
        audio_output_file = "output_audio.wav"
        record_audio_task = asyncio.to_thread(record_audio, audio_duration, audio_output_file)

        # Wait for both tasks to complete
        await asyncio.gather(capture_task, record_audio_task)

        # Merge video and audio using FFmpeg
        video_input_file = "output-video.mp4"  # Adjust the actual video file name
        audio_input_file = "output_audio.wav"  # Adjust the actual audio file name
        merged_output_file = "merged_output.mp4"  # Adjust the desired merged output file name

        ffmpeg_command = f"ffmpeg -i {video_input_file} -i {audio_input_file} -acodec aac -strict -2 -vcodec mpeg4 -qscale 2 -map 0 -map 1 {merged_output_file}"

        subprocess.run(ffmpeg_command, shell=True, check=True)
        
        print(f"Merged video and audio saved as {merged_output_file}")

# Run the main function
asyncio.run(main())
