import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def handle_crawling(target_url, working_proxies):
    print(Fore.GREEN + "Starting Crawleg...")
    # If run_sqli_auditing requires proxies, make sure to pass them
    await run_sqli_auditing(target_url, working_proxies)


async def fetch_url(session, url):
    """
    Asynchronously fetches a URL using the provided session and returns the page content and the final URL.
    Handles SSL and catches exceptions to handle errors gracefully.
    """
    try:
        async with session.get(url, ssl=False) as response:  # ssl=False can bypass SSL verification if needed
            if response.status == 200:
                text = await response.text()
                return text, str(response.url)
            else:
                print(f"Failed to fetch {url} with status {response.status}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None, None

async def crawl_page(session, url, depth, max_depth, breadth):
    """
    Recursively crawls a page up to a specified depth and breadth, and collects URLs and forms found on the pages.
    """
    if depth > max_depth:
        return [], []
    
    text, final_url = await fetch_url(session, url)
    if not text or final_url is None:
        print(f"Skipping {url} due to fetch failure.")
        return [], []
    
    soup = BeautifulSoup(text, 'html.parser')
    forms = [str(form) for form in soup.find_all('form')]
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
    results = [(final_url, forms)] if links else []

    print(f"Crawling {final_url} at depth {depth}...")  # Verbose output for each URL visited
    for link in links[:breadth]:
        full_link = urljoin(final_url, link)
        print(f"Following link from {final_url} to {full_link}")  # Verbose output for following links
        sub_results, sub_forms = await crawl_page(session, full_link, depth + 1, max_depth, breadth)
        results.extend(sub_results)

    return results, forms

async def main_crawler(target_url, depth, breadth):
    """
    Main function that sets up the session and starts the crawling process.
    Saves the crawled data temporarily and asks the user if they want to save it permanently.
    """
    async with ClientSession() as session:
        results, forms = await crawl_page(session, target_url, 0, depth, breadth)
        
        # Save to a temporary file
        with open('temp_crawled.txt', 'w') as file:
            for url, _ in results:
                file.write(f"{url}\n")
        
        # Ask if the user wants to save the results permanently
        if input("Do you want to save the results permanently? (y/n): ").lower() == 'y':
            with open(f"{target_url.replace('http://', '').replace('https://', '').replace('/', '_')}_crawled.txt", 'w') as file:
                for url, _ in results:
                    file.write(f"{url}\n")
        
        print("Crawl complete.")
        return results

# Example usage
if __name__ == '__main__':
    target_url = "http://example.com"  # A simple, openly accessible website for testing
    asyncio.run(main_crawler(target_url, 3, 10))
