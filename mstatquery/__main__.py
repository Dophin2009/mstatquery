import argparse
import sys

from lark import UnexpectedToken
from mstatquery import lib


def CliParser(default_encoding: str,
              default_format_str: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Process a Microsoft Teams meeting attendance tsv.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file',
                        help='tsv file to process')
    parser.add_argument('query', nargs='?',
                        help='filter query string')
    parser.add_argument('--encoding', dest='encoding',
                        default=default_encoding,
                        help='use an alternate encoding (default %s)'
                        % (default_encoding))
    parser.add_argument('--utf16', action='store_true',
                        help='use utf-16 encoding')
    parser.add_argument('-f', '--format', default=default_format_str,
                        help='set format string for each line (default: %s)'
                        % (default_format_str))
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable stack trace')
    return parser


def main():
    argparser = CliParser('utf-8', '{name}')
    args = argparser.parse_args()

    encoding = 'utf-16' if args.utf16 else args.encoding
    try:
        with open(args.file, encoding=encoding) as f:
            filtered = lib.filter_from_file(f, args.query)
    except UnexpectedToken as e:
        print('Invalid query entered!')
        if args.verbose:
            print('\nStack trace:\n')
            print(e)
        sys.exit(1)

    for u in filtered:
        print(args.format.format(name=u.name,
                                 first_join=u.first_joined(),
                                 last_left=u.last_left(),
                                 durations=u.durations(),
                                 total=u.total_duration(),
                                 final_status=u.final_status()))
