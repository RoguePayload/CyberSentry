import asyncio
import os
import sys
import time
from colorama import Fore, init
import importlib
from CyberSentry_ProxyChains import load_and_test_proxies
from CyberSentry_Crawler import main_crawler  # Make sure this import reflects the actual function and file names
from CyberSentry_SQLI_Auditing import run_sqli_auditing

# Initialize colorama
init(autoreset=True)

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


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


async def handle_crawl_page(target_url):
    print(Fore.GREEN + "CyberSentry Crawler")
    try:
        depth = int(input("How Deep Would You Like To Scan {MAX 10}: "))
        breadth = int(input("How Broad Would You Like To Scan {MAX 15}: "))
        depth = min(10, depth)  # Ensure max depth is 10
        breadth = min(15, breadth)  # Ensure max breadth is 15
    except ValueError:
        print(Fore.RED + "Invalid input. Using default values: Depth 3, Breadth 5.")
        depth, breadth = 3, 5
    await main_crawler(target_url, depth, breadth)
    print(Fore.GREEN + "Crawling complete. Returning to main menu...")

def display_intro():
    """Displays the introductory text and gets the target URL from the user."""
    clear_screen()
    print(Fore.BLUE + "Welcome to CyberSentry")
    print(Fore.YELLOW + "Your automated security testing toolkit.")
    print(Fore.GREEN + "Developed by RoguePayload")
    print(Fore.RED + "Warning: This tool is for authorized testing only.")
    return input(Fore.YELLOW + "Enter the target URL (e.g., https://www.mysite.com): ")

async def main_menu(target_url):
    # Load and test proxies at startup
    working_proxies = await load_and_test_proxies()
    proxy_count = len(working_proxies)  # Count of working proxies
    """Displays the main menu and handles user input."""
    while True:
        clear_screen()
        print(Fore.BLUE + "CyberSentry - Main Menu")
        print(Fore.RED + f"Target URL: {target_url}")
        if working_proxies:  # Checking if there are any working proxies
            print(Fore.GREEN + f"Using Proxies: {proxy_count}")
        else:
            print(Fore.RED + "No working proxies configured.")
        print(Fore.YELLOW + "\n1) Crawl Site & Index Pages <- Do This First!!!")
        print(Fore.CYAN + "Please Select What Test & Audit You Want AFTER Crawling The Site:")
        print(Fore.YELLOW + "2) SQL Injection Auditing")
        print(Fore.YELLOW + "3) XSS (Cross Site Scripting) Auditing")
        print(Fore.YELLOW + "4) CSRF (Cross Site Request Forgery) Auditing")
        print(Fore.YELLOW + "5) Template Injection Auditing")
        print(Fore.YELLOW + "6) RCE (Remote Code Execution) Auditing")
        print(Fore.YELLOW + "7) Runn ALL Scans Automatically")
        print(Fore.GREEN + "8) Generate Bug Report <- This is Based On Tools You Used")
        print(Fore.MAGENTA + "9) Change Target URL")
        print(Fore.RED + "10) Close Cyber Sentry")

        choice = input(Fore.CYAN + "Select an option: ")
        await handle_menu_choice(choice, target_url, working_proxies)

async def handle_menu_choice(choice, target_url, working_proxies):
    """Handles the selected menu choice more explicitly."""
    if choice == '1':
        await handle_crawl_page(target_url)
    elif choice == '2':
        await handle_sqli_auditing(target_url, working_proxies)
    elif choice == '3':
        await handle_form_injection(target_url)
    elif choice == '4':
        await handle_template_injection(target_url)
    elif choice == '5':
        await handle_xml_injection(target_url)
    elif choice == '6':
        await handle_oauth_injection(target_url)
    elif choice == '7':
        await handle_user_agents(target_url)
    elif choice == '8':
        await handle_proxy_chains(target_url)
    elif choice == '9':
        await run_all_automatically(target_url)
    elif choice == '10':
        await generate_reports(target_url)
    elif choice == '11':
        # Refresh the target URL
        new_target_url = display_intro()
        await main_menu(new_target_url)
    elif choice == '12':
        print(Fore.RED + "Exiting CyberSentry...")
        time.sleep(1)
        sys.exit()
    else:
        print(Fore.RED + "Invalid option selected. Please try again.")
        time.sleep(1)

async def handle_crawl_site(target_url):
    # Placeholder for crawling functionality
    print(Fore.GREEN + "Crawling the site...")
    # Import the module or function to handle site crawling
    try:
        crawl_module = importlib.import_module('CyberSentry_Crawler')
        await crawl_module.crawl_site(target_url)
    except ImportError:
        print(Fore.RED + "Crawling functionality not yet implemented.")
        time.sleep(1)

# Placeholder functions for other menu choices (similar to handle_crawl_site)
async def handle_sqli_auditing(target_url, working_proxies):
    # Load user agents and payloads
    user_agents = load_user_agents()  # Ensure this function returns a list of user agents
    payloads = load_sqli_payloads()   # Ensure this function returns a list of SQLi payloads
    print(Fore.MAGENTA + "Enabling Proxy Chains!")
    time.sleep(1)
    print(Fore.CYAN + "Enabling Random User Agent!")
    time.sleep(1)
    print(Fore.GREEN + "Starting SQL Injection auditing...")
    # Pass all required parameters to the function
    await run_sqli_auditing(target_url, working_proxies, user_agents, payloads)

async def handle_form_injection(target_url):
    print(Fore.GREEN + "Form Injection auditing...")
    time.sleep(1)  # Simulate task

async def handle_template_injection(target_url):
    print(Fore.GREEN + "Template Injection auditing...")
    time.sleep(1)  # Simulate task

async def handle_xml_injection(target_url):
    print(Fore.GREEN + "XML Injection auditing...")
    time.sleep(1)  # Simulate task

async def handle_oauth_injection(target_url):
    print(Fore.GREEN + "OAuth Injection auditing...")
    time.sleep(1)  # Simulate task

async def handle_user_agents(target_url):
    print(Fore.GREEN + "Managing User Agents...")
    time.sleep(1)  # Simulate task

async def handle_proxy_chains(target_url):
    print(Fore.GREEN + "Managing Proxy Chains...")
    try:
        # Importing the proxy chain management module
        proxy_module = importlib.import_module('CyberSentry_ProxyChains')
        # Executing the proxy management function
        await proxy_module.manage_proxies(target_url)
    except ImportError:
        print(Fore.RED + "Proxy management functionality not yet implemented.")
        time.sleep(1)

async def run_all_automatically(target_url):
    print(Fore.GREEN + "Running all scans automatically...")
    time.sleep(1)  # Simulate task

async def generate_reports(target_url):
    print(Fore.GREEN + "Generating reports...")
    time.sleep(1)  # Simulate task

if __name__ == '__main__':
    target_url = display_intro()
    asyncio.run(main_menu(target_url))
