import argparse
import json
import sys

from collections import OrderedDict
from parser import parse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="gamaran",
        description="Static content generator.")

    parser.add_argument(
        "template",
        nargs=1,
        help="path to template file")

    parser.add_argument(
        "data",
        nargs=1,
        help="path to data file")

    parser.add_argument(
        "result",
        nargs=1,
        help="path to result file")

    parser.add_argument(
        "-v", "--version",
        action="version",
        version='%(prog)s 1.0')

    args = parser.parse_args()
    template_path = args.template[0]
    data_path = args.data[0]
    result_path = args.result[0]

    with open(template_path) as template_file:
        template = template_file.read()

        with open(data_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        result = parse(template, data)

        with open(result_path, "w") as result_file:
            result_file.write(str(result))
