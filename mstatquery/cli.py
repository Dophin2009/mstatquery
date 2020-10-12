import argparse


def Parser(default_encoding,
           default_format_str) -> argparse.ArgumentParser:
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
