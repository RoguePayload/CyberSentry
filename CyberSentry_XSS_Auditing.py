import aiohttp
import asyncio
from urllib.parse import urljoin
import random
from colorama import Fore, init

init(autoreset=True)

def load_user_agents():
    with open('CyberSentry_USER_AGENTS.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def load_proxies():
    with open('CyberSentry_PROXY_CHAINS.txt', 'r') as file:
        return [line.strip() for line in file if 'http' in line]

def load_xss_payloads():
    with open('xss_payloads.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

async def test_xss(session, url, payload, proxy):
    try:
        target_url = urljoin(url, payload)  # Modify based on how you want to inject
        async with session.get(target_url, proxy=proxy) as response:
            if response.status == 200:
                content = await response.text()
                if "expected_change" in content:
                    return 'Positive', target_url
                return 'Potential', target_url
            return 'Negative', target_url
    except Exception as e:
        print(Fore.RED + f"Error with {target_url}: {e}")
        return 'Error', target_url

async def run_xss_auditing(urls, payloads, user_agents, working_proxies):
    results = []
    proxy_index = 0
    user_agent_index = 0

    async with aiohttp.ClientSession() as session:
        for url in urls:
            for payload in payloads:
                # Rotate user agents and proxies for each request
                proxy = working_proxies[proxy_index % len(working_proxies)] if working_proxies else None
                user_agent = user_agents[user_agent_index % len(user_agents)]
                session.headers.update({'User-Agent': user_agent})
                
                # Using proxy correctly according to its protocol
                if proxy.startswith('http'):
                    proxy_url = proxy
                else:
                    proxy_url = None  # Or handle SOCKS proxies appropriately with aiohttp-socks if necessary
                
                # Test XSS
                result, target_url = await test_xss(session, url, payload, proxy_url)
                results.append((url, payload, result, target_url))
                print_result(url, payload, result, target_url)

                # Update indices for rotation
                proxy_index += 1
                user_agent_index += 1

        # Save temporary results and offer to save them permanently
        save_temp_results(results)
        if input("Do you want to save the results permanently? (y/n): ").lower() == 'y':
            save_permanent_results(results, 'xss_results.txt')

def print_result(url, payload, result, target_url):
    color = Fore.GREEN if result == 'Positive' else Fore.MAGENTA if result == 'Potential' else Fore.RED
    print(color + f"{result}: {url} Payload: {payload} -> {target_url}")

def save_temp_results(results):
    with open('temp_xss.txt', 'w') as f:
        for url, payload, result, target_url in results:
            f.write(f"{result}: {url}, Payload: {payload}, URL: {target_url}\n")

def save_permanent_results(results, filename):
    with open(filename, 'w') as f:
        for url, payload, result, target_url in results:
            f.write(f"{result}: {url}, Payload: {payload}, URL: {target_url}\n")

if __name__ == '__main__':
    urls = ['http://example.com']  # This should be loaded from your crawler output
    payloads = load_xss_payloads()
    asyncio.run(run_xss_auditing(urls, payloads))
