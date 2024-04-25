import os
import time
from colorama import Fore, Style, init
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque

# Initialize Colorama
init(autoreset=True)

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome_screen():
    """Display the welcome screen and get the target URL."""
    clear_screen()
    print(Fore.BLUE + 'Welcome to CyberSentry: Your Automated Security Tester')
    time.sleep(0.5)
    print(Fore.RED + 'This tool is designed to automate web vulnerability scans.')
    time.sleep(0.5)
    print(Fore.GREEN + 'Developed by: Rogue Payload {Bug Bounty Hunter | Freelance Hacker}')
    time.sleep(0.5)
    target_url = input(Fore.YELLOW + 'Enter the target URL (e.g., https://mypage.social): ')
    print(Fore.YELLOW + f'Locked On Target: {target_url}')
    time.sleep(1)
    clear_screen()
    return target_url

def display_menu(target_url):
    """Display the main menu and handle user input."""
    while True:
        clear_screen()
        print(Fore.BLUE + 'TARGET URL: ' + Fore.YELLOW + target_url)
        print(Fore.BLUE + "1) URL Injection Detection")
        print(Fore.BLUE + "2) Form Injection Detection")
        print(Fore.BLUE + "3) EVERYTHING")
        print(Fore.RED + "4) Exit")
        choice = input(Fore.BLUE + "Select an option: ")

        if choice == '1':
            url_injection(target_url)
        elif choice == '2':
            form_injection(target_url)
        elif choice == '3':
            url_injection(target_url)
            form_injection(target_url)
        elif choice == '4':
            print(Fore.GREEN + "Exiting CyberSentry...")
            break
        else:
            print(Fore.RED + 'Invalid option, please choose again.')
        time.sleep(2)


def load_payloads():
    payload_types = ['SQLi', 'HTTP', 'XSS']
    payloads = {ptype: [] for ptype in payload_types}
    for ptype in payload_types:
        try:
            with open(f"{ptype.lower()}_payloads.txt", "r") as file:
                payloads[ptype] = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Warning: No file found for {ptype}, continuing with empty payload list.")
    return payloads

payloads = load_payloads()


def inject_payloads(url, payloads):
    results = []
    for category, payload_list in payloads.items():
        for payload in payload_list:
            full_url = f"{url}?test={payload}"
            print(Fore.YELLOW + f"Now Injecting URL '{full_url}' for {category}")
            try:
                response = requests.get(full_url)
                if payload_effective(response, payload, category):
                    result = {
                        'Target URL': url,
                        'Payload': payload,
                        'Type of Payload': category,
                        'Full URL + Payload': full_url
                    }
                    results.append(result)
                    print(Fore.GREEN + f"Vulnerability detected: {full_url}")
            except requests.RequestException as e:
                print(Fore.RED + f"Failed to send request to {full_url}: {e}")
    return results

def payload_effective(response, payload, type):
    """Enhanced checks to validate if the payload has triggered a vulnerability."""
    if response.status_code != 200:
        # If the status code is not 200, it might still be a vulnerability (e.g., SQLi might cause database errors reflected in 500 errors)
        if response.status_code == 500 and type == 'SQLi':
            return True  # Simplified example; a real check would need more evidence
        return False

    if type == 'XSS':
        # Check for XSS by looking for the payload echoed in the response text
        # This is simplistic; real-world XSS validation might need to execute or simulate the script in a controlled environment
        if payload in response.text:
            return True

    if type == 'SQLi':
        # Check for common SQL error messages or other indications of successful injection
        error_messages = ["You have an error in your SQL syntax;", "Warning: mysql_fetch_assoc()"]
        for error in error_messages:
            if error in response.text:
                return True

    if type == 'HTTP':
        # Example: checking for header injection
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            return True
        # Example: checking for reflected parameters in the response
        if payload in response.text:
            return True

    # Further checks can be added here for other payload types

    return False

def url_injection(target_url):
    print(Fore.GREEN + "URL Injection Detection starting...")
    payloads = load_payloads()  # Load the payloads from files
    results = inject_payloads(target_url, payloads)
    if results:
        print(Fore.GREEN + "Injection Testing Complete. Vulnerabilities found:")
        for result in results:
            print(f"Target URL: {result['Target URL']}")
            print(f"Payload: {result['Payload']}")
            print(f"Type of Payload: {result['Type of Payload']}")
            print(f"Full URL + Payload: {result['Full URL + Payload']}\n")
    else:
        print(Fore.RED + "No vulnerabilities detected.")

    # Wait for user input to continue
    input("Press any key to continue...")  # This will pause the execution until a key is pressed
    # No need for time.sleep(2) since input() is handling the pause

def form_injection(target_url):
    """Placeholder for the form injection detection feature."""
    print(Fore.GREEN + "Form Injection Detection coming soon...")
    time.sleep(2)

if __name__ == "__main__":
    target_url = welcome_screen()
    display_menu(target_url)
