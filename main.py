import json
import re


def clean(variable):
    return variable[2:-2]


def each(data, template):
    pattern = "({{#each (.*?)}}(.*?){{/each}})"
    all_each = re.findall(pattern, template, re.DOTALL)

    one_each = all_each[0]
    one_each_data = data[one_each[1]]
    one_each_template = one_each[2]
    one_each_original = one_each[0]
    one_each_result = ""

    for item in one_each_data:
        one_each_result += replace(item, one_each_template)

    return template.replace(one_each_original, one_each_result, 1)


def replace(data, template):
    variables = re.findall("{{.*?}}", template)

    for variable in variables:
        template = template.replace(variable, data[clean(variable)], 1)

    return template


if __name__ == "__main__":
    # data_path = "data/one.json"
    # template_path = "data/one.html"

    data_path = "data/collection.json"
    template_path = "data/collection.html"

    with open(data_path) as data_file, open(template_path) as template_file:
        data = json.load(data_file)
        template = template_file.read()

        print(each(data, template))
        # print(replace(data, template))
