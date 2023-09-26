import asyncio
import cv2
import numpy as np
from playwright.async_api import async_playwright
import pyaudio
import wave
import io
from PIL import Image

# Function to convert binary image data to OpenCV frame
def image_to_frame(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    return frame

# Asynchronous function to start audio recording
async def start_audio_recording(output_audio_file):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
    
    frames = []

    print("Recording audio...")
    while True:
        try:
            data = stream.read(1024)
            frames.append(data)
        except KeyboardInterrupt:
            break

    print("Finished recording audio.")

    # Save audio to a WAV file
    wf = wave.open(output_audio_file, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

async def record_webpage(html_file, output_video_file, duration_seconds=30, width=1920, height=1080):
    try:
        # Initialize Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set the viewport size (resolution)
            await page.set_viewport_size({"width": width, "height": height})
            
            # Load the HTML file
            html_file_url = "file://" + html_file.replace("\\", "/")
            await page.goto(html_file_url)
            
            # Get the page content dimensions
            dimensions = await page.evaluate("() => ({ width: document.body.scrollWidth, height: document.body.scrollHeight })")
            
            # Create a VideoWriter object to save the video
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(output_video_file, fourcc, 30.0, (width, height))
            
            # Start audio recording in the background
            audio_output_file = "output_audio.wav"
            audio_recording_task = asyncio.create_task(start_audio_recording(audio_output_file))
            
            # Record for the specified duration
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < duration_seconds:
                # Scroll the page
                await page.evaluate(f"window.scrollTo(0, {int((asyncio.get_event_loop().time() - start_time) * dimensions['height'] / duration_seconds)})")
                
                # Capture the page content as a screenshot in binary format
                screenshot_binary = await page.screenshot()
                
                # Convert binary image data to OpenCV frame
                frame = image_to_frame(screenshot_binary)
                
                # Write the frame to the video
                out.write(frame)
                
                # Sleep for a short time to maintain the recording frame rate
                await asyncio.sleep(1 / 30)
            
            # Release the VideoWriter
            out.release()
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Close the browser and stop audio recording
        if browser:
            await browser.close()
        
        if audio_recording_task:
            audio_recording_task.cancel()

if __name__ == "__main__":
    input_html_file = r"E:\recording_initial\recording\hello.html"
    output_video_file = "output_video.avi"

    # Create an event loop and run the async function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(record_webpage(input_html_file, output_video_file, duration_seconds=30))
    loop.close()
