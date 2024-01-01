#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import csv
import re
from concurrent.futures import ThreadPoolExecutor

URL = "https://1337x.to"
Query = ""

try:
    torrents = []

    def get_torrents(url, choice):
        global Query
        if choice == "1":
            with ThreadPoolExecutor() as executor:
                for i in range(1, 11):
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

        # Use list comprehension to fetch magnet links concurrently
        with ThreadPoolExecutor() as executor:
            [executor.submit(get_magnet, torrent['torrent']) for torrent in torrents]

        print("Writing to csv file...")

        # Convert array of dictionaries to CSV file
        with open(f"{Query}.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = torrents[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(torrents)

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
                torrents.append({
                    'name': name,
                    'torrent': torrent,
                    'seeds': seeds,
                    'leeches': leeches,
                    'size': size,
                })

        return True

    magnet_regex = r"magnet:([^']+)"
    
    def get_magnet(torrent):
        try:
            res = requests.get(f"{URL}{torrent}", timeout=20)
            res.raise_for_status()
            print(f"Fetched magnet link for {URL}{torrent}")
            html = res.text
            # parse html to get magnet link
            magnet = re.search(magnet_regex, html).group(0) or ""
            return magnet
        except requests.exceptions.RequestException as error:
            print(f"Error fetching magnet link for {URL}{torrent}: {error}")
            return ''

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
            get_torrents(f"{URL}/category-search/{query}/{categories[int(cat)-1]}", choice)
        else:
            get_torrents(f"{URL}/search/{query}", choice)

    elif choice == "2":
        link = input("Link: ")
        get_torrents(link, choice)

    else:
        print("Invalid choice")
        exit(1)

except Exception as err:
    print(err)
    exit(1)
