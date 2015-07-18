import json
import re


def clean(variable):
    return variable[2:-2]


def each(data, template):
    pattern = "({{#each (.*?)}}(.*?){{/each}})"
    all_each = re.findall(pattern, template, re.DOTALL)

    for one_each in all_each:
        # one_each = all_each[0]
        one_each_data = data[one_each[1]]
        one_each_template = one_each[2]
        one_each_original = one_each[0]
        one_each_result = ""

        for item in one_each_data:
            one_each_result += replace(item, one_each_template)

        template = template.replace(one_each_original, one_each_result, 1)

    return template


def compare(expected, s):
    l1 = expected.splitlines()
    l2 = s.splitlines()

    for i in range(len(l1)):
        if l1[i] != l2[i]:
            print("Line " + str(i + 1))
            print("Expected: " + repr(l1[i]))
            print("Was: " + repr(l2[i]))
            break


def replace(data, template):
    variables = re.findall("{{.*?}}", template)

    for variable in variables:
        template = template.replace(variable, data[clean(variable)], 1)

    return template


if __name__ == "__main__":
    tests = ["one", "collection", "multiple"]

    for test in tests:
        data_path = "data/each/" + test + ".json"
        template_path = "data/each/" + test + ".html"
        expected_path = "data/each/" + test + ".expected.html"

        with open(data_path) as data_file, open(template_path) as template_file:
            data = json.load(data_file)
            template = template_file.read()

            result = each(data, template)
            result = replace(data, result)

            with open(expected_path) as expected_file:
                expected = expected_file.read()
                if result == expected:
                    print(test + ": Passed")
                else:
                    print(test + ": Failed")
                    compare(expected, result)
