import asyncio
import subprocess
from playwright.async_api import async_playwright
import os
import time

# Function to capture HTML content using Playwright
animation_stopped = False

async def capture_html_content(playwright):
    global path
    browser = await playwright.chromium.launch(headless=False, slow_mo=8000)
    context = await browser.new_context(record_video_dir="./", 
                                        viewport={"width": 1920, "height": 1080}, 
                                        record_video_size={"width": 1920, "height": 1080})
    page = await context.new_page()

    file_path = "E:\\recording_initial\\recording\\hello.html"
    # await page.goto(f"file://{file_path}")
    await page.goto("https://wizzair.com/en-gb#/booking/select-flight/TIA/CRL/2023-09-16/2023-09-23/1/0/0/null")
    
    # Wait for the <audio> element to appear (adjust the selector as needed)
    await page.wait_for_selector("audio")

    # Capture audio from the <audio> element
    await page.evaluate('''() => {
        const audioElement = document.querySelector('audio'); // Adjust the selector as needed
        audioElement.captureStream = audioElement.captureStream || audioElement.mozCaptureStream;
        const audioStream = audioElement.captureStream();
        const audioTrack = audioStream.getAudioTracks()[0];
        window.audioTrack = audioTrack;
    }''')
    
    # Record video while audio is playing
    path = await page.video.path()
    await page.video.start()

    # Wait for animation or audio to stop (adjust the condition as needed)
    await wait_animation_stops(page)
    
    # Stop video recording
    await page.video.stop()

    # Close the browser context and browser
    await context.close()
    await browser.close()

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

        # Wait for the capture task to complete
        await capture_task

        # Merge video and audio using FFmpeg
        video_input_file = path  # Adjust the actual video file name
        audio_input_file = "captured_audio.wav"  # Adjust the audio file name
        merged_output_file = "merged_output.mp4"  # Adjust the desired merged output file name

        ffmpeg_command = f"ffmpeg -i {video_input_file} -i {audio_input_file} -acodec aac -strict -2 -vcodec mpeg4 -qscale 2 -map 0 -map 1 {merged_output_file}"

        subprocess.run(ffmpeg_command, shell=True, check=True)

        print(f"Merged video and audio saved as {merged_output_file}")
        if os.path.exists(video_input_file):
            os.remove(video_input_file)
        if os.path.exists(audio_input_file):
            os.remove(audio_input_file)

# Run the main function
asyncio.run(main())
