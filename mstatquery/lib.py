from typing import Callable
from typing import List
from typing import Optional
from typing import TextIO

import mstat
from mstat import User
from mstatquery.query import Parser as QueryParser


def parse_query(query: Optional[str]) -> Callable[[User], bool]:
    if query is None:
        return lambda _: True
    else:
        query_parser = QueryParser()
        return query_parser.parse(query)


def filter_from_file(f: TextIO, query: str) -> List[User]:
    query_fn = parse_query(query)
    users = mstat.read_users(f)
    return [u for u in users if query_fn(u)]
