import asyncio
import aiohttp
from aiohttp import ClientSession
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

async def test_url_injections(urls, session):
    payloads = read_payloads('http_payloads.txt')  # This function should already be defined to read payloads
    results = await perform_tests(urls, payloads, session)  # Assume perform_tests is properly set up
    return results

# This function is needed to run the above as a standalone from the main script
async def run_url_injections():
    urls = read_crawled_urls('crawled_urls.txt')  # This function should read URLs from a file
    async with aiohttp.ClientSession() as session:
        results = await test_url_injections(urls, session)
        for result in results:
            print(result)

async def fetch_url(session, url):
    try:
        async with session.get(url) as response:
            return {
                'status': response.status,
                'text': await response.text()
            }
    except Exception as e:
        return {'status': 'failed', 'text': str(e)}

async def test_url_with_payload(session, url, payload):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query.update(payload)
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query))
    result = await fetch_url(session, new_url)
    return {
        'original_url': url,
        'full_url': new_url,
        'status': result['status'],
        'content_length': len(result['text']),
        'payload': payload
    }

async def perform_tests(urls, payloads, session):
    tasks = []
    semaphore = asyncio.Semaphore(10)  # Control concurrency with a semaphore
    for url in urls:
        for payload in payloads:
            task = asyncio.create_task(test_with_semaphore(url, {'param': payload}, session, semaphore))
            tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def test_with_semaphore(url, payload, session, semaphore):
    async with semaphore:
        return await test_url_with_payload(session, url, payload)

def read_payloads(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def read_crawled_urls(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def main():
    urls = read_crawled_urls('crawled_urls.txt')  # Read crawled URLs from a file
    payloads = read_payloads('http_payloads.txt')
    async with ClientSession() as session:
        results = await perform_tests(urls, payloads, session)
        for result in results:
            print(result)

if __name__ == '__main__':
    asyncio.run(main())
