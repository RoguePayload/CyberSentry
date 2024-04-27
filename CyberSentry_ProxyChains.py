import asyncio
from colorama import Fore, init
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

# Initialize colorama
init(autoreset=True)


def format_proxy_url(proxy):
    """
    Ensures that proxy URLs include the correct scheme needed by aiohttp_socks.
    """
    if "://" in proxy:
        return proxy
    return f"http://{proxy}"  # Default to HTTP if no protocol is specified

async def test_proxy(proxy):
    """
    Tests a single proxy by trying to fetch a page through it.
    """
    try:
        connector = ProxyConnector.from_url(format_proxy_url(proxy))
        async with ClientSession(connector=connector) as session:
            async with session.get("http://httpbin.org/ip", timeout=10) as response:
                if response.status == 200:
                    print(Fore.GREEN + f"Successfully connected via {proxy}")
                    return proxy
                else:
                    print(Fore.RED + f"Failed to connect via {proxy} with status {response.status}")
    except Exception as e:
        print(Fore.MAGENTA + f"Proxy {proxy} failed with exception: {e}")
    return None

async def load_and_test_proxies():
    """
    Loads proxies from a file and tests each one.
    """
    try:
        with open('CyberSentry_PROXY_CHAINS.txt', 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("Proxy chains file not found.")
        return []

    print("Testing proxies...")
    tasks = [test_proxy(proxy) for proxy in proxies]
    valid_proxies = await asyncio.gather(*tasks)
    return [proxy for proxy in valid_proxies if proxy]

async def use_proxies(proxies):
    """
    Demonstrates how to rotate through proxies for each request.
    """
    if not proxies:
        print("No working proxies available.")
        return

    for proxy in proxies:
        try:
            connector = ProxyConnector.from_url(format_proxy_url(proxy))
            async with ClientSession(connector=connector) as session:
                async with session.get("http://example.com", timeout=10) as response:
                    print(f"Using {proxy}, got response {response.status}")
        except Exception as e:
            print(f"Error using proxy {proxy}: {e}")

async def main():
    valid_proxies = await load_and_test_proxies()
    if valid_proxies:
        print(f"Successfully connected with {len(valid_proxies)} proxies:")
        await use_proxies(valid_proxies)  # Rotate through successful proxies
    else:
        print("No working proxies found. Continuing without proxies.")

if __name__ == '__main__':
    asyncio.run(main())
