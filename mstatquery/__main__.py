import sys
from typing import Callable
from typing import Optional

import mstat
from lark import UnexpectedToken
from mstat import RecordStatus
from mstat import User
from mstatquery.cli import Parser as CliParser
from mstatquery.query import Parser as QueryParser


def parse_query(query: Optional[str]) -> Callable[[User], bool]:
    if query is None:
        return lambda _: True
    else:
        query_parser = QueryParser()
        return query_parser.parse(query)


def main():
    argparser = CliParser('utf-8', '{name}')
    args = argparser.parse_args()

    try:
        query_fn = parse_query(args.query)
    except UnexpectedToken as e:
        print('Invalid query entered!')
        if args.verbose:
            print('\nStack trace:\n')
            print(e)
        sys.exit(1)

    encoding = 'utf-16' if args.utf16 else args.encoding
    with open(args.file, encoding=encoding) as f:
        users = mstat.read_users(f)

    filtered = [u for u in users if query_fn(u)]

    for u in filtered:
        print(args.format.format(name=u.name,
                                 first_join=u.first_joined(),
                                 last_left=u.last_left(),
                                 durations=u.durations(),
                                 total=u.total_duration(),
                                 final_status=u.final_status()))
