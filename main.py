import json
import re


def clean(variable):
    return variable[2:-2]


def each(data, template):
    pattern = "({{#each (.*?)}}(.*){{/each}})"
    all_each = re.findall(pattern, template, re.DOTALL)
    print("#EACH ---- ")
    print(all_each)

    for one_each in all_each:
        # one_each = all_each[0]
        one_each_data = data[one_each[1]]
        one_each_template = one_each[2]
        one_each_original = one_each[0]
        one_each_result = ""

        for item in one_each_data:
            print("ITEM: " + str(item))
            one_each_template = each(item, one_each_template)
            one_each_result += variables(item, one_each_template)

        template = template.replace(one_each_original, one_each_result, 1)
    print("/EACH ---- ")
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


def variables(data, template):
    # print(data)
    # print(template)
    variables = re.findall("{{[^#/].*?}}", template)
    # print(variables)

    for variable in variables:
        template = template.replace(variable, data[clean(variable)], 1)

    return template


def scope(data, template, level):
    # print("==== LEVEL " + str(level) + " ====")
    start = "{{#each "
    end = "{{/each}}"
    buff = ""
    state = 0
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
            # print(buff)
            # print(len(buff))
            # Tag.
            tag_start_index = index - (len(buff) - 1)
            tag_end_index = template.find("}}", tag_start_index) + len("}}")
            tag = template[tag_start_index:tag_end_index]
            # print("Tag:" + tag + " " + str(tag_start_index) + " to " + str(tag_end_index))

            # Get data key from the tag.
            key = tag[len(start): -2]
            # print("Key:" + key)

            # Get template used for the next scope.
            # This is from where the tag ends to the end.
            template_part = template[tag_end_index:]

            # print("++++ template_part +++++")
            # print(template_part)
            # print("+++++++++")
            # print(template[:tag_start_index])
            # print("+++++++++")

            loop_result = ""
            # Time to do the loop part of the each function.
            for item in data[key]:
                # print(item)
                scope_result, scope_end_index = scope(item, template_part, level + 1)
                loop_result += scope_result
            #    template = template[:i] + t
            #    index = index + len(t)

            # Need to replace the content from the start tag to the end tag.
            # With what we got from the scope result.
            # However we also need to get the position of the end tag because
            # this is unknown in the current scope.
            # Then update the index.

            # I think there is a shift somewhere...
            template_start = template[:tag_start_index]
            template_end = template[tag_end_index + scope_end_index + 1:]
            template = template_start + loop_result + template_end
            index = len(template_start + loop_result)

            # print("----- new template ----")
            # print(index)
            # print(template)
            # print("---- / new template -----")

            # Empty the buffer.
            buff = ""
        elif buff == end:
            # print(str(index) + ": " + buff)
            to_replace = template[:index - (len(buff) - 1)]
            # print("//////////////")
            # print(to_replace)
            # print("//////////////")
            template = variables(data, to_replace)
            # print(template)
            # print("//////////////")
            if level > 0:
                # print("==== END LEVEL " + str(level) + " ====")
                return template, index
        else:
            index += 1

    template = variables(data, template)

    return template, index


if __name__ == "__main__":
    # "one",, "multiple", "nested"
    tests = ["one", "collection", "multiple", "nested"]

    for test in tests:
        data_path = "data/each/" + test + ".json"
        template_path = "data/each/" + test + ".html"
        expected_path = "data/each/" + test + ".expected.html"
        result_path = "data/each/" + test + ".result.html"

        with open(data_path) as data_file, open(template_path) as template_file:
            data = json.load(data_file)
            template = template_file.read()

            scope_result, scope_end_index = scope(data, template, 0)
            result = scope_result
            # print(scope_end_index)
            # print("###:: " + scope_result)
            # result = each(data, template)
            # result = variables(data, result)
            # print(result)

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
