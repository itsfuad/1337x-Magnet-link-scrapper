import aiohttp
import asyncio
import undetected_chromedriver as selenium


url = "https://www.x1337x.se/"

async def start():
    cf_clearance = ".qftT5zprqt.3ampo.oki0lCStqnFf2YmIbuUDMGMhk-1707565747-1-AROluPSj0JpniA7QTiZZZCfhrJYsvkUmJcl0dEmLQc4M7D1g9RESqE+ZX1AQ0lgXGc7qxs/wKEFEoTGVedqABr8="
    cookies = {
        "cf_clearance": cf_clearance
    }
    async with aiohttp.ClientSession(cookies=cookies) as session:
        try:

            response = await session.get(url)
            if response.status != 200:
                print(f"Error: {response.status}")
                return
            else:
                print(f"Success: {response.status}")

        except Exception as e:
            print(f"Error: {e}")
            return

asyncio.run(start())
