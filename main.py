import json
import re


def clean(variable):
    return variable[2:-2]


def compare(expected, s):
    l1 = expected.splitlines()
    l2 = s.splitlines()

    for i in range(len(l1)):
        if l1[i] != l2[i]:
            print("Line " + str(i + 1))
            print("Expected: " + repr(l1[i]))
            print("Was: " + repr(l2[i]))
            break


def variables(data, template):
    variables = re.findall("{{[^#/].*?}}", template)

    for variable in variables:
        template = template.replace(variable, data[clean(variable)], 1)

    return template


def scope(data, template, level):
    start = "{{#each "
    end = "{{/each}}"
    buff = ""
    index = 0

    while index < len(template):
        # Get next character.
        c = template[index]
        # Append character to the buffer.
        buff += c
        # Trim the buffer if it's greater then what we need
        if len(buff) > len(end):
            buff = buff[1:]

        # Calculate current state.
        if buff[:len(start)] == start:
            # Tag.
            tag_start_index = index - (len(buff) - 1)
            tag_end_index = template.find("}}", tag_start_index) + len("}}")
            tag = template[tag_start_index:tag_end_index]

            # Get data key from the tag.
            key = tag[len(start): -2]

            # Get template used for the next scope.
            # This is from where the tag ends to the end.
            template_part = template[tag_end_index:]

            loop_result = ""
            # Time to do the loop part of the each function.
            for item in data[key]:
                scope_result, scope_end_index = scope(item, template_part, level + 1)
                loop_result += scope_result

            # Replace the tag and it's content witht the scope results.
            # TODO: I think there is a shift somewhere...
            template_start = template[:tag_start_index]
            template_end = template[tag_end_index + scope_end_index + 1:]
            template = template_start + loop_result + template_end

            # Update index.
            index = len(template_start + loop_result)

            # Empty the buffer.
            buff = ""
        elif buff == end:
            template_part = template[:index - (len(buff) - 1)]
            template = variables(data, template_part)
            if level > 0:
                return template, index
        else:
            index += 1

    template = variables(data, template)

    return template, index


if __name__ == "__main__":
    tests = ["one", "collection", "multiple", "nested"]

    for test in tests:
        data_path = "data/each/" + test + ".json"
        template_path = "data/each/" + test + ".html"
        expected_path = "data/each/" + test + ".expected.html"
        result_path = "data/each/" + test + ".result.html"

        with open(data_path) as data_file, open(template_path) as template_file:
            data = json.load(data_file)
            template = template_file.read()

            result, index = scope(data, template, 0)

            with open(expected_path) as expected_file:
                expected = expected_file.read()
                print("---")
                if result == expected:
                    print(test + ": Passed")
                else:
                    print(test + ": Failed")
                    compare(expected, result)

            with open(result_path, "w") as result_file:
                result_file.write(result)
                print("Result stored: " + result_path)
