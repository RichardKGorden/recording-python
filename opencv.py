import asyncio
from playwright.async_api import async_playwright
import cv2
import numpy as np

async def capture_html_content(playwright):
    browser = await playwright.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()

    # Replace 'your_url_here' with the URL of the HTML content you want to capture.
    file_path = "E:\\recording_initial\\recording\\hello.html"
    await page.goto(f"file://{file_path}")

    frames_per_second = 60 
    # Set up OpenCV video writer
    width, height = 1920, 1080  # Adjust the dimensions as needed
    writer = cv2.VideoWriter("output_video.avi", cv2.VideoWriter_fourcc(*"XVID"), 60, (width, height))
    
    # Capture frames and save them to the video
    while True:  # Capture 300 frames (adjust as needed)
        # Capture a screenshot from the page
        screenshot = await page.screenshot()
        
        image = cv2.imdecode(
            np.frombuffer(screenshot, dtype=np.uint8), cv2.IMREAD_COLOR
        )
      
        writer.write(image)
        
        cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
        # Resize this window
        cv2.resizeWindow("Live", 480, 270)

        cv2.imshow('Live', image)
	
        # Stop recording when we press 'q'
        if cv2.waitKey(1) == ord('q'):
            break
        # Release the video writer
    writer.release()

        # Close the Playwright browser context
    await context.close()

async def main():
    async with async_playwright() as playwright:
        await capture_html_content(playwright)

if __name__ == "__main__":
    asyncio.run(main())
