import asyncio
from playwright.async_api import async_playwright

async def run(playwright):
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(record_video_dir="videos/",viewport={"width": 1920, "height": 1080},record_video_size={"width": 1920, "height": 1080})
    page = await context.new_page()
    
    file_path = "E:\\recording_initial\\recording\\hello.html"
    await page.goto(f"file://{file_path}")

    await context.close()
async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())