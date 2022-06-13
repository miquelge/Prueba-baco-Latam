from datetime import datetime


async def screenshot(page):
    await page.screenshot({'path': f'screenshot-{datetime.now}.png'})
