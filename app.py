#!/usr/bin/env python
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
# import re
import random
import string
import time

URL = "https://www.1337xx.to"
Query = ""
torrents = {}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

async def get_torrents(url: str, choice: str, max_pages: int):
    global Query
    # start timer
    start = time.time()
    print("Getting torrents...")
    if choice == "1":
        # Get torrents concurrently
        async with aiohttp.ClientSession() as session:
            tasks = [get_html(session, f"{url}/{i}/") for i in range(1, max_pages + 1)]
            await asyncio.gather(*tasks)

    elif choice == "2":
        async with aiohttp.ClientSession() as session:
            page_number = int(url.split('/')[-2])
            # fetch pages from page_number to page_number + max_pages
            url = url.replace(f'/{page_number}/', '')
            tasks = [get_html(session, f"{url}/{i}/") for i in range(page_number, page_number + max_pages)]
            await asyncio.gather(*tasks)

    # if torrents is empty
    if len(torrents) == 0:
        print("No torrents found. Skipping further steps...")
        exit(1)

    print(f"Getting {len(torrents)} magnet links...")

    # Get magnet links concurrently
    async with aiohttp.ClientSession() as session:
        tasks = [get_magnet(session, torrent) for torrent in torrents.values()]
        await asyncio.gather(*tasks)

    # Write to csv file
    csv_filename = f"{Query or random_string()}.csv"
    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["Name", "Torrent", "Magnet", "Seeds", "Leeches", "Size"])
        for torrent in torrents.values():
            writer.writerow([torrent["name"], torrent["torrent"], torrent["magnet"], torrent["seeds"], torrent["leeches"], torrent["size"]])

    print(f"Saved to {csv_filename}")
    print(f"Time taken: {time.time() - start} seconds")

async def get_html(session, url):
    #print(f"Getting torrents from {url}")

    async with session.get(url, headers=headers) as response:
        #print("Parsing data...")
        soup = BeautifulSoup(await response.text(), 'html.parser')

        rows = soup.select("tbody > tr")

        # .../.../..../1/  the number is at the end
        page = int(url.split('/')[-2])

        print(f"Found {len(rows)} torrents in page {page}")

        if len(rows) == 0:
            return None

        for row in rows:
            item = row.select(".coll-1 > a")[1]
            name = item.get_text(strip=True)
            torrent = item.get("href")
            seeds = row.select_one(".coll-2").get_text(strip=True)
            leeches = row.select_one(".coll-3").get_text(strip=True)
            size = row.select_one(".coll-4").get_text(strip=True)

            if item:
                torrents[name] = {
                    "name": name,
                    "torrent": URL+torrent,
                    "seeds": seeds,
                    "leeches": leeches,
                    "size": size,
                }

        return True

async def get_magnet(session, torrent):
    try:
        async with session.get(f"{torrent['torrent']}", headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            # parse html to get magnet link 'a[href^="magnet:"]'
            magnet = soup.select_one('a[href^="magnet:"]').get("href") if soup.select_one('a[href^="magnet:"]') else html
            # update torrent object
            #print(f"Got magnet link for {torrent['name']}")
            #print(f'Magnet: {magnet}\n\n')
            torrents[torrent['name']]['magnet'] = magnet
    except aiohttp.ClientError as error:
        print(f"Error fetching magnet link: {error}")
        torrents[torrent['name']]['magnet'] = "N/A"

def random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

categories = [
    "Movies",
    "TV",
    "Games",
    "Music",
    "Apps",
    "Anime",
    "Documentaries",
]

choice = input("Search by: \n1. Keyword / Name (Eg. Horror Movie, Bat Man)\n2. Link (Eg. https://1337.to/......)\n")

url = ""
if choice == "1":
    query = input("Search: ")
    Query = query
    print("Categories:\n")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")
    cat = input(f"Category: [1-{len(categories)}]\n")
    if cat:
        if not 1 <= int(cat) <= len(categories):
            print("Invalid category")
            exit(1)
        url = f"{URL}/category-search/{query}/{categories[int(cat)-1]}"
    else:
        url = f"{URL}/search/{query}"

elif choice == "2":
    url = input("Link: ")
        # if page doesn't end with /
    if not url.endswith('/'):
        print("Invalid link. Link should end with '/'")
        exit(1)
else:
    print("Invalid choice")
    exit(1)

max_pages = input("Max pages to fetch: ")
if not max_pages or int(max_pages) < 1:
    print("Invalid max pages. Fetching 10 pages as default.")
    max_pages = 10
else:
    max_pages = int(max_pages)

asyncio.run(get_torrents(url, choice, max_pages))


