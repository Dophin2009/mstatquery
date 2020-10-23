# Microsoft Teams Meeting Attendance Log Query

A tool that lets you filter and list the users who attended a Microsoft
Teams meeting by parsing the attendance log.

## Installation

This project uses Python Poetry:

    $ git clone https://github.com/stogacs/mstatquery.git
    $ cd mstatquery
    $ poetry install

## Usage

Example:

    $ mstatquery 2020-09-29.csv 'total >= (00:40:00) or final_status == joined'
    John Doe
    Filip Marks
    Andre Munro
    Jon Faulkner
    Jordana Carey
    Bryn Dyer
    Kelsea Davie
    Kayan Giles
    Kairon Vang

Pass `-h` or `--help` to show options:

    $ mstatquery -h
    usage: mstatquery [-h] [--encoding ENCODING] [--utf16] [-f FORMAT] [-v] file [query]

    Process a Microsoft Teams meeting attendance tsv.

    positional arguments:
      file                  tsv file to process
      query                 filter query string

    optional arguments:
      -h, --help            show this help message and exit
      --encoding ENCODING   use an alternate encoding (default utf-8)
      --utf16               use utf-16 encoding
      -f FORMAT, --format FORMAT
                            set format string for each line; ignored if --csv is enabled
      -v, --verbose         enable stack trace

## License

This project is licensed under the terms of the MIT license. See
[LICENSE](./LICENSE) for details.
