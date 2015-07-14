import json
import re


def clean(variable):
    return variable[2:-2]


def replace(data, template):
    variables = re.findall("{{.*?}}", template)

    for variable in variables:
        template = template.replace(variable, data[clean(variable)], 1)

    return template


if __name__ == "__main__":
    with open("data/one.json", "r") as data_file, open("data/one.html") as template_file:
        data = json.load(data_file)
        template = template_file.read()
        print(replace(data, template))
