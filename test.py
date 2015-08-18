import json
import os
from collections import OrderedDict
from parser import parse


def compare(expected, s):
    l1 = expected.splitlines()
    l2 = s.splitlines()
    result = ""

    for i in range(len(l1)):
        if l1[i] != l2[i]:
            result += "\tLine:     " + str(i + 1) + "\n"
            result += "\tExpected: " + repr(l1[i]) + "\n"
            result += "\tWas:      " + repr(l2[i]) + "\n"
            break

    return result


def run_test(package, test):
    # Create a message through the test for printing later.
    message = package + "/" + test + "\n"
    passed = False

    # Paths
    data_path = "tests/{0}/{1}/data.json".format(package, test)
    template_path = "tests/{0}/{1}/template.html".format(package, test)
    expected_path = "tests/{0}/{1}/expected.html".format(package, test)
    result_path = "tests/{0}/{1}/result.html".format(package, test)

    with open(template_path) as template_file:
        template = template_file.read()

        if os.path.isfile(data_path):
            with open(data_path) as data_file:
                data = json.load(data_file)
        else:
            data = []

        result = parse(template, data)

        # Store the result for easier viewing when a test fails.
        with open(result_path, "w") as result_file:
            result_file.write(str(result))

        # Validate the test.
        with open(expected_path) as expected_file:
            expected = expected_file.read()
            if result == expected:
                passed = True
            else:
                passed = False
                message += compare(expected, result)

        return passed, message


if __name__ == "__main__":
    packages = OrderedDict()
    packages["global"] = ["single"]
    packages["each"] = [
        "empty",
        "collection",
        "this",
        "multiple",
        "twice",
        "nested",
        "else",
        "none",
        "index"
    ]
    packages["with"] = ["single", "none"]
    packages["comments-dashed"] = [
        "begin-newline",
        "begin-spaces",
        "begin-tabs",
        "endline",
        "inline",
        "multiline",
        "preserve-newline",
        "special-tokens"
    ]
    packages["comments-simple"] = [
        "begin-newline",
        "begin-spaces",
        "begin-tabs",
        "endline",
        "inline",
        "multiline",
        "preserve-newline"
    ]
    packages["if"] = ["true", "false", "else"]
    packages["unless"] = ["true", "false", "else"]

    all_passed = True
    for package, tests in packages.items():
        for test in tests:
            passed, message = run_test(package, test)
            if not passed:
                print(message)
                all_passed = False

    if all_passed:
        print("All tests passed.")
