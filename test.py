import json
import time
from parser import parse, Section, Tag


def compare(expected, s):
    l1 = expected.splitlines()
    l2 = s.splitlines()

    for i in range(len(l1)):
        if l1[i] != l2[i]:
            print("\tLine " + str(i + 1))
            print("\tExpected: " + repr(l1[i]))
            print("\tWas: " + repr(l2[i]))
            break


def run_test(package, test):
    # Start a timer for execution time.
    start = time.clock()

    print(package + "/" + test)

    # Paths
    data_path = "tests/{0}/{1}/data.json".format(package, test)
    template_path = "tests/{0}/{1}/template.html".format(package, test)
    expected_path = "tests/{0}/{1}/expected.html".format(package, test)
    result_path = "tests/{0}/{1}/result.html".format(package, test)

    with open(data_path) as data_file, open(template_path) as template_file:
        data = json.load(data_file)
        template = template_file.read()

        # Initiate the parsen with the global as the most outer scope.
        # result, index = parse(data, template, 0)
        s = Tag("html", 0, 0)
        e = Tag("html", len(template), len(template))
        section = None
        section = Section(s, e)
        result = parse(template, section)
        result = result.combine(template, data)

        # Display time it took to execute the test.
        print("\tTime: " + str(time.clock() - start))

        # Store the result for easier viewing for cases when a test fails.
        with open(result_path, "w") as result_file:
            result_file.write(str(result))
            print("\tResult: " + result_path)

        # Validate the test.
        with open(expected_path) as expected_file:
            expected = expected_file.read()
            if result == expected:
                print("\tPassed")
            else:
                print("\tFailed")
                compare(expected, result)

        print("")


if __name__ == "__main__":
    packages = {
        "global": ["single"],
        "each": [
            "empty",
            "collection",
            "this",
            "multiple",
            "twice",
            "nested",
            "else"
        ]
    }

    for package, tests in packages.items():
        for test in tests:
            run_test(package, test)
