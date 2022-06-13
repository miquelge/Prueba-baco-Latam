import asyncio
import os

from dotenv import load_dotenv

from scrappers.BandCampScrapper import BandCampScrapper


async def main():
    load_dotenv(".env")
    user = os.environ.get('USERNAME_BANDCAMP')
    password = os.environ.get('PASSWORD_BANDCAMP')
    scrapper = BandCampScrapper(user, password)
    await scrapper.login()
    scrapper.process()

asyncio.get_event_loop().run_until_complete(main())
