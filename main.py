import argparse
import json
import os

from collections import OrderedDict
from parser import parse


def generate(template_path, data_path, result_path, clean):
    with open(template_path) as template_file:
        template = template_file.read()

        with open(data_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        result = parse(template, data, args.clean)

        with open(result_path, "w") as result_file:
            result_file.write(str(result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="gamaran",
        description="Static content generator.")

    parser.add_argument(
        "-v", "--version",
        action="version",
        version='%(prog)s 1.0')

    parser.add_argument(
        "--clean",
        action="store_true",
        help="remove indentation to the left of tags when on an empty line")

    parser.add_argument(
        "--config",
        nargs=1,
        metavar="FILE PATH",
        action="store",
        help="generate multiple files from a given config")

    parser.add_argument(
        "--generate",
        nargs=3,
        metavar=("TEMPLATE", "DATA", "RESULT"),
        action="store",
        help="generate a single file without the need of a setup config, specify each argument as a relative path to the config")

    args = parser.parse_args()

    if args.generate:
        template_path = args.generate[0]
        data_path = args.generate[1]
        result_path = args.generate[2]
        generate(template_path, data_path, result_path, args.clean)

    elif args.config:
        with open(args.config[0], "r") as config:
            folder = os.path.dirname(os.path.realpath(args.config[0]))
            options = config.read()
            options = [s for s in options.splitlines() if s.strip()]

            for i in range(0, len(options), 3):
                template_path = os.path.join(folder, options[i])
                data_path = os.path.join(folder, options[i + 1])
                result_path = os.path.join(folder, options[i + 2])
                generate(template_path, data_path, result_path, args.clean)

    else:
        print("Specify on of the two options --generate or --config.")
