import sys

from lark import UnexpectedToken
from mstatquery import lib
from mstatquery.cli import Parser as CliParser


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
