import asyncio
import pyaudio
import wave
import subprocess
from playwright.async_api import async_playwright
import os
import time
# Function to capture HTML content using Playwright
animation_stopped=False
async def capture_html_content(playwright):
    global path
    browser = await playwright.chromium.launch(headless=False,slow_mo=8000)
    context = await browser.new_context(record_video_dir="./", 
                                        viewport={"width": 1920, "height": 1080}, 
                                        record_video_size={"width": 1920, "height": 1080})
    page = await context.new_page()

    file_path = "E:\\recording_initial\\recording\\hello.html"
    # await page.goto(f"file://{file_path}")
    # await page.goto("https://www.gyan.dev/ffmpeg/builds/")
    await page.goto("https://wizzair.com/en-gb#/booking/select-flight/TIA/CRL/2023-09-16/2023-09-23/1/0/0/null")
    await page.wait_for_timeout(4000)
    if(await wait_animation_stops(page)):
        await context.close()
        await browser.close()
    # page.wait_for_selector("script[src=dist/reveal.js]")
    # Add code here to capture HTML content (e.g., take a screenshot or record video)
    path=await page.video.path()
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
    # for i in range(0, int(sample_rate / chunk * audio_duration)):
    while True:
        audio_data = audio_stream.read(chunk)
        audio_frames.append(audio_data)
        audio_wavefile.writeframes(audio_data)
        if animation_stopped:
            break

    # Close audio stream and file
    audio_stream.stop_stream()
    audio_stream.close()
    audio_wavefile.close()
    audio.terminate()

    print("Audio recording completed.")

async def wait_animation_stops(page, timeout=30):
    global animation_stopped
    t = time.time()
    old_image = await page.screenshot(full_page=True)
    while time.time() - t < timeout:
        time.sleep(0.5)
        new_image = await page.screenshot(full_page=True)
        if old_image == new_image:
            print(f'Animation stopped after {time.time() - t} seconds')
            animation_stopped = True
            return True
        old_image = new_image
    print(f'Animation did not stop in {timeout} seconds')
    return False

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
        video_input_file = path  # Adjust the actual video file name
        audio_input_file = "output_audio.wav"  # Adjust the actual audio file name
        merged_output_file = "merged_output.mp4"  # Adjust the desired merged output file name

        # ffmpeg_command = f"ffmpeg -i {video_input_file} -i {audio_input_file} -c:v copy -c:a aac -strict experimental {merged_output_file}"
        # ffmpeg_command = f"ffmpeg -fflags +genpts -i {video_input_file} -r 24 1.mp4"
        # ffmpeg_command = f"ffmpeg -i {video_input_file} -i {audio_input_file} -map 0:0 -map 1:0 {merged_output_file}"
        ffmpeg_command = f"ffmpeg -i {video_input_file} -i {audio_input_file} -acodec aac -strict -2 -vcodec mpeg4 -qscale 2 -map 0 -map 1 {merged_output_file}"
        
        subprocess.run(ffmpeg_command, shell=True, check=True)
        
        print(f"Merged video and audio saved as {merged_output_file}")
        if os.path.exists(video_input_file):
            os.remove(video_input_file)
        if os.path.exists(audio_input_file):
            os.remove(audio_input_file)
# Run the main function
asyncio.run(main())
