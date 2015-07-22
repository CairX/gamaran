import re

debug = False


def log(string):
    if debug:
        print(string)


def clean(variable):
    return variable[2:-2]


def variables(data, template):
    tags = re.findall("{{[^#/].*?}}", template)

    for tag in tags:
        variable = clean(tag)
        if variable == "this":
            d = data
        else:
            d = data[variable]
        template = template.replace(tag, d, 1)

    return template


def scope(data, template, level):
    log("----- # Level " + str(level) + " -----")

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
            log("Key: " + key)

            # Get template used for the next scope.
            # This is from where the tag ends to the end.
            template_part = template[tag_end_index:]

            loop_result = ""

            # Time to do the loop part of the each function.
            if data[key]:
                for item in data[key]:
                    scope_result, scope_end_index = scope(item, template_part, level + 1)
                    loop_result += scope_result
            else:
                scope_result, scope_end_index = scope({}, template_part, level + 1)
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
            if data:
                template = variables(data, template_part)
            else:
                template = ""

            log("----- / Level " + str(level) + " -----")
            if level > 0:
                return template, index
        else:
            index += 1

    template = variables(data, template)

    return template, index
