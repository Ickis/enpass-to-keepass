#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert an Enpass export file so it can be imported to a KeePass database using KeePassXC

Documentation & Issues: https://github.com/jsphpl/enpass-to-keepass

License: Public Domain
Author: Joseph Paul <joseph@sehrgute.software>
"""

import argparse
import csv

ALLOWED_FIELDS = ['url', 'username', 'password']
HEADERS = ['title', 'url', 'username', 'password', 'notes']
MAP_FIELDNAMES = {
    'login': 'username',
    'benutzername': 'username',
    'login kennwort': 'password',
    'kennwort': 'password',
    'email': 'username',
    'e-mail': 'username',
}

extra_keys = set([])

def main(args):
    results = []
    reader = csv.reader(args.input_file)

    reader.__next__() # skip titles row

    for row in reader:
        results.append(processRow(row))

    if (len(results) == 0):
        print('No rows to write (empty input file?)')
        return

    print('%d rows processed' % len(results))
    print('Writing to %s' % args.output_file.name)
    if (len(extra_keys) > 0):
        print('Found extra keys: ' + ', '.join(extra_keys))

    writer = csv.DictWriter(args.output_file, HEADERS)
    writer.writeheader()
    writer.writerows(results)


def processRow(row):
    notes = row.pop()
    result = {
        'title': row.pop(0),
        'notes': notes + '\n\n' if len(notes) else ''
    }

    for (key, value) in makePairs(row):
        if key in result or key not in ALLOWED_FIELDS:
            result['notes'] += "%s: %s\n" % (key, value)
            extra_keys.add(key)
        else:
            result[key] = value

    return result


def makePairs(row):
    return [(sanitizeKey(row[i]), row[i+1]) for i in range(0, len(row), 2)]

def sanitizeKey(key):
    key = key.strip().lower()

    if key in MAP_FIELDNAMES:
        return MAP_FIELDNAMES[key]

    return key

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input_file', type=argparse.FileType('r'),
                        help='Path to Enpass csv export file')
    parser.add_argument('output_file', type=argparse.FileType('w'),
                        help='Path to output file (csv)')
    main(parser.parse_args())
