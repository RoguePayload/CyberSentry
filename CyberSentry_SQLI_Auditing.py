import aiohttp
import asyncio
from urllib.parse import urljoin
import random
from colorama import Fore, init
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession

init(autoreset=True)

def load_user_agents():
    user_agents = []
    try:
        with open('CyberSentry_USER_AGENTS.txt', 'r') as file:
            user_agents = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("User agents file not found.")
    except Exception as e:
        print(f"Failed to load user agents: {e}")
    return user_agents

def load_sqli_payloads():
    payloads = []
    try:
        with open('sqli_payloads.txt', 'r') as file:
            payloads = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print("SQLi payloads file not found.")
    except Exception as e:
        print(f"Failed to load SQLi payloads: {e}")
    return payloads

def load_proxies():
    """
    Loads only HTTP/HTTPS proxies from 'CyberSentry_PROXY_CHAINS.txt'.
    """
    proxies = []
    try:
        with open('CyberSentry_PROXY_CHAINS.txt', 'r') as file:
            proxies = [line.strip() for line in file if line.strip() and ('http://' in line or 'https://' in line)]
        print("Loaded HTTP/HTTPS proxies:", proxies)  # Print loaded proxies for verification
    except FileNotFoundError:
        print("Error: 'CyberSentry_PROXY_CHAINS.txt' file not found.")
    except Exception as e:
        print(f"An error occurred while loading proxies: {e}")
    return proxies

async def check_proxy(proxy):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://httpbin.org/ip", proxy=proxy) as response:
                if response.status == 200:
                    print(f"Proxy {proxy} is working")
                else:
                    print(f"Proxy {proxy} returned status {response.status}")
        except Exception as e:
            print(f"Proxy {proxy} failed with error: {e}")


def select_proxy(proxies, current_index):
    """
    Selects a proxy from a list, cycling through them based on the current index.
    Returns the selected proxy and the updated index.
    """
    if not proxies:
        return None, current_index  # Return None if there are no proxies

    selected_proxy = proxies[current_index % len(proxies)]
    current_index = (current_index + 1) % len(proxies)  # Update the index for next call
    return selected_proxy, current_index

async def fetch_url(session, url, proxy=None):
    """
    Fetches content from a URL using the provided session and optional proxy.
    This function handles both HTTP/HTTPS and SOCKS proxies.
    """
    try:
        # Adjust the SSL verification here
        if proxy and (proxy.startswith('socks4://') or proxy.startswith('socks5://')):
            connector = ProxyConnector.from_url(proxy, ssl=False)  # Disable SSL verification
            async with aiohttp.ClientSession(connector=connector) as socks_session:
                async with socks_session.get(url, ssl=False) as response:  # Disable SSL verification
                    return await response.text(), response.status, str(response.url)
        else:
            async with session.get(url, proxy=proxy, ssl=False) as response:  # Disable SSL verification
                return await response.text(), response.status, str(response.url)
    except Exception as e:
        print(f"Error fetching {url} with proxy {proxy}: {e}")
        return None, None, None

async def test_sqli(session, base_url, payload, proxy=None):
    """
    Tests a single URL with a SQL injection payload, using an optional proxy.
    Returns a result tuple indicating success, potential, or failure.
    """
    url = urljoin(base_url, payload)
    original_content, _, _ = await fetch_url(session, base_url, proxy)
    modified_content, status, final_url = await fetch_url(session, url, proxy)

    # Assess the results
    if status == 200:
        original_size = len(original_content) if original_content else 0
        modified_size = len(modified_content) if modified_content else 0
        content_changed = original_content != modified_content
        size_changed = original_size != modified_size

        # Determine the result based on the changes
        if content_changed and size_changed:
            return 'Positive', final_url  # Major changes suggest a successful injection
        elif content_changed or size_changed:
            return 'Possible', final_url  # Some changes suggest a potential vulnerability
        else:
            return 'Negative', final_url  # No changes suggest no vulnerability
    return 'Inconclusive', final_url  # Non-200 status or other issues

async def run_sqli_auditing(target_url, working_proxies, user_agents, payloads):
    results = []
    proxy_index = 0
    user_agent_index = 0
    request_count = 0

    # Create the initial session
    async with aiohttp.ClientSession() as session:
        for url in [target_url]:  # Expand this to handle multiple URLs if necessary
            for payload in payloads:
                # Rotate proxy and user agent every 10 requests
                if request_count % 10 == 0:
                    if working_proxies:  # Ensure there are proxies to use
                        proxy = working_proxies[proxy_index % len(working_proxies)]
                        proxy_index += 1
                    else:
                        proxy = None

                    user_agent = user_agents[user_agent_index % len(user_agents)]
                    user_agent_index += 1

                    # Update session headers for proxy and user agent
                    session.headers.update({'User-Agent': user_agent})
                    if proxy:
                        if proxy.startswith('socks4://') or proxy.startswith('socks5://'):
                            # Re-create session with a SOCKS proxy if necessary
                            connector = ProxyConnector.from_url(proxy)
                            session = aiohttp.ClientSession(connector=connector)
                        else:
                            session = aiohttp.ClientSession()
                            session.headers.update({'Proxy': proxy})

                # Perform SQL Injection test
                is_positive, final_url = await test_sqli(session, url, payload, proxy)
                result_line = f"{url},{payload},{final_url},{'Positive' if is_positive else 'Potential'}\n"
                results.append(result_line)
                print_result(url, payload, final_url, is_positive)

                request_count += 1

        # Close the session if using aiohttp-socks
        await session.close()

        # Save results temporarily
        temp_filename = "temp_sqli.txt"
        with open(temp_filename, 'w') as temp_file:
            temp_file.writelines(results)
        print("Temporary results saved.")

        # Ask user if they want to save results permanently
        if input("Do you want to save the results permanently? (y/n): ").lower() == 'y':
            permanent_filename = f"{target_url.replace('http://', '').replace('https://', '').replace('/', '_')}_sqli_results.txt"
            with open(permanent_filename, 'w') as file:
                file.writelines(results)
            print(f"Results saved permanently in {permanent_filename}.")

        print("Returning to the main menu...")

def print_result(url, payload, final_url, result):
    """
    Prints each SQLi result with color coding based on the result type.
    """
    colors = {
        'Positive': Fore.GREEN,
        'Possible': Fore.MAGENTA,
        'Negative': Fore.RED,
        'Inconclusive': Fore.YELLOW
    }
    color = colors.get(result, Fore.WHITE)
    print(f"{color}| {url} | {payload} | {final_url} | {result} |")

def save_results(results):
    with open('sqli_results.txt', 'w') as f:
        for result in results:
            f.write(f"{result[0]},{result[1]},{result[2]},{result[3]}\n")
