#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import csv
import re
from concurrent.futures import ThreadPoolExecutor

URL = "https://1337x.to"
Query = ""

try:
    torrents = {}

    def get_torrents(url, choice, max_pages=10):
        global Query
        if choice == "1":
            with ThreadPoolExecutor() as executor:
                for i in range(1, max_pages+1):
                    futures = [executor.submit(get_html, f"{url}/{i}/")]
                    if not futures[0].result():
                        if i == 1:
                            print("No torrents found")
                            exit(1)
                        else:
                            print("No more torrents found")
                            break

        elif choice == "2":
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(get_html, url)]
                if not futures[0].result():
                    print("No torrents found")
                    exit(1)

        print(f"Getting {len(torrents)} magnet links...")

        # Get magnet links concurrently
        with ThreadPoolExecutor() as executor:
            for torrent in torrents.values():
                executor.submit(get_magnet, torrent)

        print("Writing to csv file...")

        # Write to csv file
        with open(f"{Query}.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Torrent", "Magnet", "Seeds", "Leeches", "Size"])
            for torrent in torrents.values():
                writer.writerow([torrent["name"], torrent["torent"], torrent["magnet"], torrent["seeds"], torrent["leeches"], torrent["size"]])
                
        print("Done")

    def get_html(url):
        print(f"Getting torrents from {url}")
        res = requests.get(url)
        # time.sleep(1)
        print("Parsing data...")
        soup = BeautifulSoup(res.text, 'html.parser')

        rows = soup.select("tbody > tr")

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
                    "torent": torrent,
                    "seeds": seeds,
                    "leeches": leeches,
                    "size": size,
                }

        return True
    
    
    def get_magnet(torrent):
        try:
            res = requests.get(f"{URL}{torrent['torent']}", timeout=20)
            res.raise_for_status()
            html = res.text
            # parse html to get magnet link
            magnet = re.search(r'magnet:?.+?"', html).group(0).rstrip('"') or "N/A"
            # update torrent object
            print(f"Got magnet link for {torrent['name']}")
            torrents[torrent['name']]['magnet'] = magnet
        except requests.exceptions.RequestException as error:
            print(f"Error fetching magnet link for {URL}{torrent}: {error}")
            torrents[torrent['name']]['magnet'] = "N/A"

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
            #get_torrents(f"{URL}/category-search/{query}/{categories[int(cat)-1]}", choice)
            url = f"{URL}/category-search/{query}/{categories[int(cat)-1]}"
        else:
            #get_torrents(f"{URL}/search/{query}", choice)
            url = f"{URL}/search/{query}"

    elif choice == "2":
        url = input("Link: ")

    else:
        print("Invalid choice")
        exit(1)

    max_pages = input("Max pages: (Default: 10)\n")
    if max_pages:
        max_pages = int(max_pages)
        if not 1 <= max_pages <= 15:
            print("Invalid max pages")
            exit(1)
    else:
        max_pages = 10

    get_torrents(url, choice, max_pages)

except Exception as err:
    print(err)
    exit(1)