import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import os
from colorama import Fore, init
import random

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def post_crawl_interaction(crawled_urls, target_url):
    # Process the crawled URLs
    if input(Fore.YELLOW + "Save crawled results to a file? (y/n): ").lower() == 'y':
        filename = f"{target_url.replace('http://', '').replace('https://', '').replace('/', '_')}_crawled.txt"
        save_results(crawled_urls, filename)
    print(Fore.GREEN + "Crawling complete. Results processed.")

def read_proxies(file_path):
    try:
        with open(file_path, 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        print(Fore.RED + "Proxy file not found.")
        return None

def read_user_agents(file_path='cybersentry_user_agents.txt'):
    try:
        with open(file_path, 'r') as file:
            user_agents = [line.strip() for line in file if line.strip()]
        return user_agents
    except FileNotFoundError:
        print(Fore.RED + "User agents file not found. Using default user agent.")
        return ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3']


async def fetch(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status in [301, 302]:
                return await fetch(session, response.headers['Location'], headers)
            elif response.status == 200:
                return await response.text()
            return None
    except Exception as e:
        print(Fore.RED + f"Error fetching {url}: {e}")
        return None

async def main_crawler(target_url, max_depth, breadth_depth, proxies=None):
    user_agents = read_user_agents()  # Read user agents from file
    random_user_agent = random.choice(user_agents)
    headers = {'User-Agent': random_user_agent}
    
    # Setting up the HTTP connector and session
    connector = aiohttp.TCPConnector(limit_per_host=breadth_depth)
    timeout = aiohttp.ClientTimeout(total=30)  # Set an appropriate timeout

    # Decide on proxy usage
    proxy = random.choice(proxies) if proxies else None

    visited = set()
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        await crawl(session, target_url, max_depth, 0, visited, headers, proxy)
    return visited

# Recursive crawling function
async def crawl(session, url, max_depth, current_depth, visited, headers, proxy=None):
    if current_depth > max_depth or url in visited:
        return

    print(f"Crawling: {url} at depth {current_depth}")
    visited.add(url)
    try:
        async with session.get(url, proxy=proxy) as response:
            if response.status == 200:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                links = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True) if link.get('href')]
                tasks = [asyncio.create_task(crawl(session, link, max_depth, current_depth + 1, visited, headers, proxy)) for link in links]
                await asyncio.gather(*tasks)
            elif response.status in [301, 302]:  # Handle redirects
                new_url = response.headers.get('Location')
                if new_url:
                    await crawl(session, urljoin(url, new_url), max_depth, current_depth, visited, headers, proxy)
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def save_results(urls, filename):
    with open(filename, 'w') as file:
        for url in urls:
            file.write(url + '\n')

async def run_crawler(start_url, max_depth, breadth_depth, respect_robots, proxies=None):
    user_agents = read_user_agents()  # Assumes this function reads user agents from a file
    random_user_agent = random.choice(user_agents)  # Select a random user agent for this session
    headers = {'User-Agent': random_user_agent}
    visited = set()
    
    connector = TCPConnector(limit_per_host=breadth_depth)
    timeout = ClientTimeout(total=60)  # Define a total timeout for all operations

    # Check if proxies are provided and pick one randomly
    if proxies:
        proxy = random.choice(proxies)
    else:
        proxy = None

    # Using the chosen proxy in the session
    async with ClientSession(connector=connector, timeout=timeout, headers=headers) as session:
        await crawl(session, start_url, max_depth, 0, visited, headers, proxy=proxy)
    return visited

def crawler_interface(target_url):
    clear_screen()
    print(Fore.BLUE + "Cyber Sentry Crawler")
    asyncio.sleep(1.3)
    print(Fore.YELLOW + f"Locked On {target_url}")
    asyncio.sleep(1.5)
    crawl_depth = int(input(Fore.YELLOW + "How Deep Would You Like To Crawl: "))
    breadth_depth = int(input(Fore.YELLOW + "The Breadth of the Crawl: "))
    print(Fore.YELLOW + f"Do you want to use Proxy Chains? (y/n): ", end='')
    use_proxy = input().strip().lower() == 'y'
    proxies = None
    if use_proxy:
        proxy_file = input(Fore.YELLOW + "Please enter the path to your proxy chain file: ")
        proxies = read_proxies(proxy_file)
    auto_or_custom = int(input(Fore.YELLOW + "Automatic Crawl or Custom URL Patterns (1-Auto | 2-Custom): "))
    if auto_or_custom == 2:
        url_patterns = input(Fore.YELLOW + "Please Input the Directory Location of Your URL Patterns: ")  # Consider how you will use these patterns
    respect_robots = input(Fore.YELLOW + "Toggle robots.txt Directives? (y|n): ").lower() == 'y'
    user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3']
    
    urls_collected = asyncio.run(run_crawler(target_url, crawl_depth, breadth_depth, user_agents, respect_robots))
    if input(Fore.YELLOW + "Save crawled results to a file? (y/n): ").lower() == 'y':
        save_results(urls_collected, f"{target_url.replace('https://', '').replace('http://', '').replace('/', '_')}_crawled.txt")
    return urls_collected
