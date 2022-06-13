import json
import re
from typing import List

import requests
from bs4 import BeautifulSoup
from pyppeteer import launch
from retrying import retry
from utils import screenshot

from scrappers.AbstractScrappingClass import AbstractScrappingClass

MAX_LOGIN_RETRIES = 2
WAIT_TIME_RETRIES = 5000  # 5 seconds


class BandCampScrapper (AbstractScrappingClass):
    baseURL = "https://bandcamp.com"

    def __init__(self, user, password) -> None:
        super().__init__()
        self.session = requests.Session()
        self.user = user
        self.password = password
        self.wishListAlbums = []
        self.followingArtistsLabels = []
        self.followingGenres = set()
        self.reliability = None

    @retry(
        stop_max_attempt_number=MAX_LOGIN_RETRIES,
        wait_fixed=WAIT_TIME_RETRIES
    )
    async def login(self):
        try:
            # Launch puppeteer
            browser = await launch()
            print('Browser Launched')
            page = await browser.newPage()
            print('Page Created')

            # Go to Log In page
            await page.goto(self.baseURL)
            await page.click('a[href="https://bandcamp.com/login?from=home"]')
            await page.waitForSelector('#username-field')

            # Fill credentials and click login button
            userField = await page.querySelector('#username-field')
            await page.evaluate(f"(el) => el.value = '{self.user}'", userField)
            await page.evaluate(
                "(el) => { el.dispatchEvent(new Event('change'));}", userField
            )
            passField = await page.querySelector('#password-field')
            await page.evaluate(
                f"(el) => el.value = '{self.password}'", passField
            )
            await page.evaluate(
                "(el) => { el.dispatchEvent(new Event('change'));}", passField
            )
            submitButton = await page.querySelector('button[type="submit"]')
            await page.evaluate(
                "(el) => el.removeAttribute('disabled')", submitButton
            )
            await submitButton.click()
            await page.waitForSelector('#menubar')

            # Get cookies for session and close
            cookies = await page.cookies()
            await browser.close()

            # Format and put cookies in session
            session = requests.Session()
            for cookie in cookies:
                session.cookies.set_cookie(
                    requests.cookies.create_cookie(
                        name=cookie.get('name', ""),
                        value=cookie.get('value', ""),
                        domain=cookie.get('domain', "")
                    )
                )
        except Exception as e:
            await browser.close()
            screenshot(page)
            raise e

    def process(self):
        self.__get_wish_list_albums()
        self.__get_following_artists_labels()
        self.__get_following_genres()
        self.__calculate_reliability()
        self.__print_info()

    def __get_wish_list_albums(self):
        response = self.session.get(f"{self.baseURL}/{self.user}/wishlist")
        soup = BeautifulSoup(response.text, 'html.parser')
        wishListContainer = soup.find("div", {"id": "wishlist-items"})
        wishListElements = wishListContainer.findAll(
            'li', id=re.compile('^collection-item-container_')
        )
        for element in wishListElements:
            self.__format_wish_list_album(element)

    def __format_wish_list_album(self, element) -> dict:
        album = dict()
        album['name'] = element.find(
            "div", {"class": "collection-item-title"}
        ).text
        artist = element.find("div", {"class": "collection-item-artist"}).text
        album['artist'] = artist.replace('by ', '')
        album['tags'] = self.__get_album_tags(
            element.find("a", {"class": "item-link"})['href']
        )
        self.wishListAlbums.append(album)

    def __get_album_tags(self, url) -> List[str]:
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tagElements = soup.find_all("a", {"class": "tag"})
        return list(map(lambda x: x.text, tagElements))

    def __get_following_artists_labels(self):
        response = self.session.get(
            f"{self.baseURL}/{self.user}/following/artists_and_labels"
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find("div", {"id": "following-bands-container"})
        bandItems = container.findAll(
            'li', id=re.compile('^follow-grid-item-band_')
        )
        for element in bandItems:
            self.followingArtistsLabels.append(
                element.find('a', {"class": "fan-username"}).text
            )

    def __get_following_genres(self):
        response = self.session.get(
            f"{self.baseURL}/{self.user}/following/genres"
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        container = soup.find("div", {"id": "following-genres-container"})
        bandItems = container.findAll(
            'li', id=re.compile('^follow-grid-item-genre_')
        )
        for element in bandItems:
            self.followingGenres.add(
                element.find('a', {"class": "genre-name"}).text
            )

    def __calculate_reliability(self):
        reliables = list(
            filter(lambda x: self.__is_reliable(x), self.wishListAlbums)
        )
        self.reliability = (len(reliables)/len(self.wishListAlbums))*100

    def __is_reliable(self, album):
        return any(x in self.followingGenres for x in album['tags'])

    def __print_info(self):
        print("Wishlist Albums:")
        for album in self.wishListAlbums:
            print(json.dumps(album, indent=4))
        print("Following Artists & Labels")
        print(self.followingArtistsLabels)
        print("Following Genres")
        print(self.followingGenres)
        print(f"Reliability: {self.reliability}%")
