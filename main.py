import json
import sys

from collections import OrderedDict
from parser import parse


if __name__ == "__main__":
    template_path = sys.argv[1]
    data_path = sys.argv[2]
    result_path = sys.argv[3]

    with open(template_path) as template_file:
        template = template_file.read()

        with open(data_path) as data_file:
            data = json.load(data_file, object_pairs_hook=OrderedDict)

        result = parse(template, data)

        with open(result_path, "w") as result_file:
            result_file.write(str(result))
