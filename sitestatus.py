import os
import sys
import argparse
import pathlib
import pandas as pd
import openpyxl
from http.client import HTTPConnection
from urllib.parse import urlparse


def look_through_excel_file():
    # read by default 1st sheet of an excel file
    url = pd.read_excel('urls.xlsx')
    print(url)
    pass


def site_is_online(url, timeout=2):
    """Return True if the target URL is online.

    Raise an exception otherwise.
    """
    error = Exception("unknown error")
    parser = urlparse(url)
    host = parser.netloc or parser.path.split("/")[0]
    for port in (80, 443):
        connection = HTTPConnection(host=host, port=port, timeout=timeout)
        try:
            connection.request("HEAD", "/")
            return True
        except Exception as e:
            error = e
        finally:
            connection.close()
    raise error


def read_user_cli_args():
    parser = argparse.ArgumentParser(
        prog="sitestatus", description="Let's check the availability of websites with the options below"
    )
    # ...
    parser.add_argument(
        "-f",
        "--input-file",
        metavar="<file_name>",
        type=str,
        default="",
        help="Use argumnent to read URLs from a file",
    )
    parser.add_argument(
        "-u",
        "--urls",
        metavar="URLs",
        nargs="+",
        type=str,
        default=[],
        help="Enter one or more website URLs after this argument",
    )
    return parser.parse_args()


def _get_websites_urls(user_args):
    urls = user_args.urls
    if user_args.input_file:
        urls += _read_urls_from_file(user_args.input_file)
    return urls


def _read_urls_from_file(file):
    file_path = pathlib.Path(file)
    if file_path.is_file():
        with file_path.open() as urls_file:
            urls = [url.strip() for url in urls_file]
            print(f"Read {len(urls)} URLs from {file}")
            print(f"This are the URLs in file:\n")
            for url in urls:
                print(f"  {url}\n")
            if urls:
                return urls
            print(f"Error: empty input file, {file}", file=sys.stderr)
    else:
        print("Error: input file not found", file=sys.stderr)
    return []


def _synchronous_check(urls):
    for url in urls:
        error = ""
        try:
            result = site_is_online(url)
        except Exception as e:
            result = False
            error = str(e)
        display_check_result(result, url, error)


def display_check_result(result, url, error=""):
    """Display the result of a connectivity check."""
    print(f'The status of "{url}" is:', end=" ")
    if result:
        print('"Online!" 👍')
    else:
        print(f'"Offline?" 👎 \n  Error: "{error}"')


def main():
    look_through_excel_file()
    user_args = read_user_cli_args()
    urls = _get_websites_urls(user_args)
    if not urls:
        print("Error: no URLs to check", file=sys.stderr)
        sys.exit(1)
    _synchronous_check(urls)


if __name__ == "__main__":
    main()
