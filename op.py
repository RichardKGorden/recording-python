import asyncio
from playwright.async_api import async_playwright
import cv2
import numpy as np

async def record_html_content(url, output_video_file, duration_seconds=10):
    # Initialize Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate to the web page
        html_file_url = "file://" + url.replace("\\", "/")
        await page.goto(html_file_url,timeout=30000)
        # await page.wait_for_selector("canvas")

        # Prepare to record frames
        frames = []

        # Capture frames at a high rate for the specified duration
        for _ in range(int(duration_seconds * 30)):  # 30 frames per second
            # Capture a screenshot
            screenshot = await page.screenshot()
		
            # Convert the screenshot to a NumPy array
            screenshot_np = np.frombuffer(screenshot, dtype=np.uint8)
            frame = cv2.imdecode(screenshot_np, flags=cv2.IMREAD_COLOR)

            # Append the frame to the list
            frames.append(frame)

            # Sleep briefly between frames
            await asyncio.sleep(1 / 30)

        # Create a VideoWriter to save the frames as a video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        width, height = frames[0].shape[1], frames[0].shape[0]
        out = cv2.VideoWriter(output_video_file, fourcc, 30, (width, height))

        # Write frames to the video
        for frame in frames:
            out.write(frame)

        # Release the VideoWriter
        out.release()

        # Close the browser
        await browser.close()

if __name__ == "__main__":
    url_to_record = r"E:\recording_initial\recording\hello.html"  # Replace with your target URL
    output_video_file = "output.mp4"
    recording_duration_seconds = 10  # Adjust as needed

    asyncio.run(record_html_content(url_to_record, output_video_file, recording_duration_seconds))
