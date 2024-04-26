import asyncio
from CyberSentry_Crawling import main_crawler, post_crawl_interaction
from CyberSentry_URL_Payloads import run_url_injections
import os
import time
from colorama import Fore, init
import importlib 

# Initialize colorama
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def display_intro():
    clear_screen()
    print(Fore.BLUE + "CyberSentry")
    time.sleep(0.8)
    print(Fore.YELLOW + "Your automated security testing toolkit.")
    time.sleep(0.8)
    print(Fore.GREEN + "Developed by RoguePayload")
    time.sleep(0.8)
    print(Fore.RED + "Warning: This tool is for authorized testing only.")
    time.sleep(1.2)
    target_url = input(Fore.YELLOW + "What is our Target: ")
    print(Fore.YELLOW + f"Locked on Target: {target_url}")
    time.sleep(0.8)
    return target_url

async def main_menu(target_url):
    while True:
        clear_screen()
        print(Fore.BLUE + "CyberSentry")
        print(Fore.RED + f"Target URL: {target_url}")
        print(Fore.RED + "^^VICTIM HAS NO CLUE WE ARE COMING!!!^^")
        print(Fore.BLUE + "Primary Menu:")
        print(Fore.BLUE + "1) Crawl Site & Index Pages <- Start HERE For OPTIMIZATION of the Program!")
        print(Fore.GREEN + "Let's Undress This Site And See What They Are Hiding Behind That...Dress??? No Mask!!!")
        print(Fore.BLUE + "2) URL Injection Auditing <- Inject Various HTTP Payloads Automatically!")
        print(Fore.GREEN + "We Get It... We Got Tired Of Manual Injections Too. The Coder Is Also Just As Lazy!!!")
        print(Fore.BLUE + "3) Form Injection Auditing <- Testing ALL Form Input Fields Discovered")
        print(Fore.GREEN + "Yes. There Are Hundreds Of Potential Form Inputs. That Is Why I Exist So You Go Get That Coffee!!!")
        print(Fore.BLUE + "4) Template Injection Auditing <- Testing against various Templates for each site!")
        print(Fore.GREEN + "No! I Will Not Hack Your Site...Said No Hacker Ever...")
        print(Fore.BLUE + "5) XML Injection Auditing <- Page/URL Hijacking & other Functions!")
        print(Fore.GREEN + "Yea, We Are Lazy Too! That Is Why RoguePayload Built Me!")
        print(Fore.BLUE + "6) OAuth Injection Auditing <- Want to bypass the OAuth page?")
        print(Fore.GREEN + "It is kinda like lock picking...But digital...Right?")
        print(Fore.GREEN + "7) Report Generator <- Automatically Generate a Report Based On Your Work!!!")
        print(Fore.GREEN + "We appreciate if you kept the name of tool + dev name, but we understand... Your the {HACKER_MAN/WOMAN}")
        print(Fore.YELLOW + "8) Change Target URL <- Tired of this Target Already?")
        print(Fore.GREEN + "So am I! Let us Find Another Channel To Watch!")
        print(Fore.RED + "9) Exit <- Close the Program")
        print(Fore.GREEN + "Wait... Are You Really Tired Of Me Already? We Just Started Having...Hacking Fun?!?!?!")
        choice = input(Fore.YELLOW + "Select an option: ")
        await handle_menu_choice(choice, target_url)

async def handle_menu_choice(choice, target_url):
    module_name = ""
    function_name = ""
    if choice == '1':
        # Get crawl settings from user
        max_depth = int(input(Fore.YELLOW + "Enter the maximum depth for crawling: "))
        breadth_depth = int(input(Fore.YELLOW + "Enter the maximum number of concurrent connections: "))
        
        use_proxies = input(Fore.YELLOW + "Do you want to use proxies? (y/n): ").lower() == 'y'
        proxies = None
        if use_proxies:
            proxy_file = input(Fore.YELLOW + "Enter the path to your proxy file: ")
            proxies = read_proxies(proxy_file)  # Ensure this function reads proxies from the specified file

        # Run the crawler with the provided settings
        crawled_urls = await main_crawler(target_url, max_depth, breadth_depth, proxies)
        await post_crawl_interaction(crawled_urls, target_url)
    if choice == '2':
        await run_url_injections()  # Call the function to run URL injections
    elif choice == '3':
        module_name = "CyberSentry_FormInjection_Payloads"
        function_name = "test_form_injections"
    elif choice == '4':
        module_name = "CyberSentry_Template_Payloads"
        function_name = "test_form_templates"
    elif choice == '5':
        module_name = "CyberSentry_XML_Payloads"
        function_name = "test_form_xml"
    elif choice == '6':
        module_name = "CyberSentry_OAuth_Payloads"
        function_name = "test_oauth"
    elif choice == '7':
        module_name = "CyberSentry_Report_Generator"
        function_name = "report_generator"
    elif choice == '8':
        target_url = display_intro() # Refresh the program to change the Target URL
        await main_menu(target_url)
        return
    elif choice == '9':
        print(Fore.RED + "Shutting Down Systems... ")
        time.sleep(1.3)
        exit(0)
        return
    else:
        print(Fore. CYAN + "{Payload_Injection} Coming Soon")
        time.sleep(1.3)
        return

    # Continue mapping all menu items to their respective modules and functions

    # Dynamically load and execute the selected module and function
    if module_name and function_name:
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        await function(target_url)

if __name__ == '__main__':
    target_url = display_intro()
    asyncio.run(main_menu(target_url))

