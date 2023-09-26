import asyncio
from playwright.sync_api import sync_playwright

async def main():
    async with sync_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # HTML 파일 로드
        file_path = "E:\\recording_initial\\recording\\hello.html"
        await page.goto(f"file://{file_path}")

        # 비디오 녹화 시작
        video_path = "output.mp4"
        await page.start_recording(path=video_path, options={"width": 1920, "height": 1080})

        # 페이지가 완료될 때까지 대기
        await page.wait_for_selector("body")

        # 비디오 녹화 중지
        await page.stop_recording()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
