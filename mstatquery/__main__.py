import argparse
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import List

import mstat
from lark import Lark
from lark import Transformer
from lark import UnexpectedToken
from lark import v_args
from mstat import RecordStatus
from mstat import User

default_encoding = 'utf-8'

query_grammar = r"""
    ?start      : boolexpr

    boolexpr    : boolexpr "and" boolexpr   -> op_and
                | boolexpr "or" boolexpr    -> op_or
                | "(" boolexpr ")"
                | value binop value         -> boolexpr_op

    binop       : "=="              -> eq
                | "!="              -> ne
                | "<="              -> le
                | ">="              -> ge
                | "<"               -> lt
                | ">"               -> gt
                | "%"               -> contains

    value       : ident
                | status
                | duration
                | timestamp
                | string
                | number
                | "true"            -> true
                | "false"           -> false

    ident       : "name"            -> ident_name
                | "first_join"      -> ident_first_join
                | "last_left"       -> ident_last_left
                | "durations"       -> ident_durations
                | "total"           -> ident_total
                | "final_status"    -> ident_final_status
    status      : "joined"          -> status_joined
                | "left"            -> status_left

    string      : ESCAPED_STRING
    number      : SIGNED_NUMBER
    timestamp   : "(" /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/ ")"
    duration    : "(" /\d{2}:\d{2}:\d{2}/ ")"

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.WS

    %ignore WS
"""


@v_args(inline=True)
class QueryTransformer(Transformer):
    def __init__(self):
        Transformer.__init__(self, visit_tokens=True)

    def boolexpr_op(self, a, op, b) -> Callable[[User], bool]:
        def f(u):
            return op(a(u), b(u))
        return f

    def op_and(self, a, b) -> Callable[[User], bool]:
        return lambda u: a(u) and b(u)

    def op_or(self, a, b) -> Callable[[User], bool]:
        return lambda u: a(u) or b(u)

    # Operators
    def eq(self):
        return lambda a, b: a == b

    def ne(self): return lambda a, b: a != b
    def le(self): return lambda a, b: a <= b
    def ge(self): return lambda a, b: a >= b
    def lt(self): return lambda a, b: a < b
    def gt(self): return lambda a, b: a > b
    def contains(self): return lambda a, b: b in a

    # Terminal values
    def value(self, v) -> Callable[[User], str]:
        return v

    def ident_name(self) -> Callable[[User], str]:
        return lambda u: u.name

    def ident_first_join(self) -> Callable[[User], datetime]:
        return lambda u: u.first_joined()

    def ident_last_left(self) -> Callable[[User], datetime]:
        return lambda u: u.last_left()

    def ident_durations(self) -> Callable[[User], List[timedelta]]:
        return lambda u: u.durations()

    def ident_total(self) -> Callable[[User], timedelta]:
        return lambda u: u.total_duration()

    def ident_final_status(self) -> Callable[[User], RecordStatus]:
        return lambda u: u.final_status()

    def status_joined(self) -> Callable[[User], RecordStatus]:
        return lambda _: RecordStatus.JOINED

    def status_left(self) -> Callable[[User], RecordStatus]:
        return lambda _: RecordStatus.LEFT

    def string(self, s: str) -> Callable[[User], str]:
        return lambda _: s[1:-1]

    def number(self, n: str) -> Callable[[User], float]:
        return lambda _: float(n)

    def timestamp(self, t: str) -> Callable[[User], datetime]:
        return lambda _: datetime.strptime(t, "%Y-%m-%d %H:%M:%S")

    def duration(self, t: str) -> Callable[[User], timedelta]:
        split = [float(f) for f in t.split(':')]
        return lambda _: timedelta(hours=split[0], minutes=split[1],
                                   seconds=split[2])

    def true(self) -> Callable[[User], bool]:
        return lambda _: True

    def false(self) -> Callable[[User], bool]:
        return lambda _: False


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Process a Microsoft Teams meeting attendance tsv.')
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
    parser.add_argument('-f', '--format', default='{name}',
                        help='set format string for each line; '
                        'ignored if --csv is enabled')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='enable stack trace')
    return parser


def main():
    argparser = parser()
    args = argparser.parse_args()

    query_parser = Lark(query_grammar, parser='lalr')

    if args.query is not None:
        try:
            tree = query_parser.parse(args.query)
            print(tree.pretty())
            query_func = QueryTransformer().transform(tree)
        except UnexpectedToken as e:
            print("Invalid query entered!")
            if args.verbose:
                print(e)
            return
    else:
        def query_func(_): return True

    encoding = 'utf-16' if args.utf16 else args.encoding
    with open(args.file, encoding=encoding) as f:
        users = mstat.read_users(f)

    filtered = [u for u in users if query_func(u)]

    for u in filtered:
        print(args.format.format(name=u.name,
                                 first_join=u.first_joined(),
                                 last_left=u.last_left(),
                                 durations=u.durations(),
                                 total=u.total_duration(),
                                 final_status=u.final_status()))
