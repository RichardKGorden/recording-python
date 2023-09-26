import asyncio
import cv2
import pyppeteer
import numpy 

async def record_html_to_video(html_file, output_file, duration_seconds):
    browser = await pyppeteer.launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({'width': 1920, 'height': 1080}) 

    frames_per_second = 30  
    writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"XVID"), frames_per_second, (1920, 1080))

    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    await page.setContent(html_content)
    
    for _ in range(int(duration_seconds * frames_per_second)):
        screenshot = await page.screenshot()
        image = cv2.imdecode(
            numpy.frombuffer(screenshot, dtype=numpy.uint8), cv2.IMREAD_COLOR
        )
        writer.write(image)

        await asyncio.sleep(1 / frames_per_second)

    writer.release()
    await browser.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(record_html_to_video("E:\\recording_initial\\recording\\hello.html", "output_video.avi", 10))

