import re

debug = False


class Tag:
    def __init__(self, tag, start, end, key=None):
        self.tag = tag
        self.start = start
        self.end = end
        self.key = key

    def __str__(self):
        s = "Tag: "
        s += repr(self.tag)
        s += " ("
        s += str(self.start)
        s += ", "
        s += str(self.end)
        s += ")"
        return s


class Section:
    def __init__(self, start, end=None):
        self.start = start
        self.end = end
        self.sections = []

    def __str__(self):
        s = "Section: "
        s += " Start " + str(self.start)
        s += " End " + str(self.end)
        s += " # " + str(len(self.sections))
        return s

    def template(self, template):
        self.part_inner = template[self.start.end:self.end.start]
        self.part_outer = template[self.start.start:self.end.end]

    def add(self, section):
        self.sections.append(section)

    def printSections(self, level):
        tabs = "\t" * level
        print(tabs + str(self))
        for s in self.sections:
            s.printSections(level+1)

    # def part(self, template):
    def data(self, template, data):
        if self.start.tag == "html":
            # print("KEY: html")
            d = data
            tmp = template
            for s in self.sections:
                t = s.data(template, d)
                tmp = tmp.replace(s.part_outer, t, 1)
            tmp = variables(d, tmp)
            return tmp
        else:
            # print("KEY: " + str(self.start.key))
            d = data[self.start.key]

            i_r = ""
            for i in d:
                # tmp = self.part_inner
                # print("=== i ===")
                # print(i)
                s_r = self.part_inner
                for s in self.sections:
                    # print("=== s ===")
                    # print(s)
                    # print("--- === ---")
                    t = s.data(template, i)
                    # print(t)
                    s_r = s_r.replace(s.part_outer, t, 1)
                    # print(s_r)
                    #print(self.part_inner.replace(s.part_outer, t, 1))
                    # print("=== /s ===")
                # print("=== /i ===")
                # print("--- r ---")
                # print(i)
                # print("--- /r ---")
                i_r += variables(i, s_r)

            # print(i_r)
            return i_r


def log(string):
    if debug:
        print(string)


def clean(variable):
    return variable[2:-2]


def variables(data, template):
    #print("=== VAR ===")
    #print(data)
    #print(template)
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


each_tag_start = "{{#each "
each_tag_start_end = "}}"
each_tag_end = "{{/each}}"


def get_start_tag(template, index):
    tag_start = template.find(each_tag_start, index)
    tag_end = template.find(each_tag_start_end, tag_start) + len(each_tag_start_end)

    if tag_start == -1 or tag_end == -1:
        return None
    else:
        tag = template[tag_start:tag_end]
        key_start = tag_start + len(each_tag_start)
        key_end = tag_end - len(each_tag_start_end)
        key = template[key_start:key_end]

        return Tag(tag, tag_start, tag_end, key)
        # {
        #     "tag_start": tag_start,
        #     "tag_end": tag_end,
        #     "tag": tag,
        #     "key": key,
        # }


def get_end_tag(template, index):
    tag_start = template.find(each_tag_end, index)

    if tag_start == -1:
        return None
    else:
        tag_end = tag_start + len(each_tag_end)
        tag = template[tag_start:tag_end]

        return Tag(tag, tag_start, tag_end)
        # {
        #     "tag_start": tag_start,
        #     "tag_end": tag_end,
        #     "tag": tag,
        # }


def parse(data, template, index):
    #print(template)
    # print(data)
    print("Index: " + str(index))
    original_index = index

    # if index > 0:
    #     i = template.find(each_tag_start_end, index) + len(each_tag_start_end)
    #     start_tag = get_start_tag(template, i)
    # else:
    #     start_tag = get_start_tag(template, index)


    start_tag = get_start_tag(template, index)
    print("Start tag: " + str(start_tag))
    nested_tag = None
    if start_tag:
        nested_tag = get_start_tag(template, start_tag.end)
        print("Nested tag: " + str(nested_tag))
        # x = template.find(start_tag.tag, index)
        #print("Find: " + str(x))
        # print("Find: " + str(start_tag.start))
        # if index == start_tag.start:
        #     print("NESTED")
        #     nested_tag = get_start_tag(template, start_tag.end)
        #     print("Nested tag: " + str(nested_tag))

    if nested_tag:
        print("Nested tag: " + str(nested_tag.tag))
        # tag_start_index = nested
        # tag_end_index = template.find(start_end, tag_start_index) + len(start_end)
        # tag = template[tag_start_index:tag_end_index]
        # print(repr(tag))
        # key = template[tag_start_index + len(start):template.find(start_end, tag_start_index)]
        # print(repr(key))
        # template, index = parse(data[key], template, nested)
        # print(data)

        new = ""
        for item in data[start_tag.key]:
            template, index = parse(item, template, start_tag.end)
            # new += template
        print(index)
        print(template)
        # start_tag = nested_tag
    elif start_tag:
        print("Else if")
        print(start_tag.tag)

        # has_end = template.find(each_tag_end, index)
        # if has_end != -1:
        #     new = ""
        #     part = template[template.find(each_tag_start_end, index) + len(each_tag_start_end):has_end]
        #     #print(part)
        #     for item in data:
        #         #print(item)
        #         new += variables(item, part)
        #
        #     template = template.replace(template[index:has_end + len(end)], new, 1)

        end_tag = get_end_tag(template, start_tag.end)
        #if end_tag:
        print("End tag: " + str(end_tag.tag))
        new = ""
        part = template[start_tag.end:end_tag.start]
        # print(part)
        # print(data)
        for item in data[start_tag.key]:
            print(item)
            new += variables(item, part)

        # template[index:has_end + len(end)]
        template = template.replace(template[start_tag.start:end_tag.end], new, 1)
        index = end_tag.end

    else:
        print("Else")

    template = variables(data, template)

    return template, index


def another(template, section):
    index = section.start.end
    print("+++")
    print(section)

    while index < len(template):
        print("--- " + str(index))
        start_tag = get_start_tag(template, index)
        end_tag = get_end_tag(template, index)

        if start_tag:
            nested_tag = get_start_tag(template, start_tag.end)
            # end_tag = get_end_tag(template, start_tag.end)
        else:
            nested_tag = None
            # end_tag = get_end_tag(template, index)

        print("Start tag: " + str(start_tag))
        print("Nested tag: " + str(nested_tag))
        print("End tag: " + str(end_tag))

        if nested_tag and nested_tag.start < end_tag.start:
            print("Nested")
            new = Section(nested_tag)
            new = another(template, new)
            # print(new)
            index = new.end.end
            section.add(new)

        if start_tag:
            print("Start")
            end_tag = end_tag = get_end_tag(template, index)
            print("End tag: " + str(end_tag))
            new = Section(start_tag, end_tag)
            index = new.end.end
            section.add(new)

        elif end_tag:
            # else:
            print("End")
            section.end = end_tag
            # index = section.end.end
            return section
        else:
            print("Else")
            index = section.end.end

    "Natural return"
    return section


def again(template, section):

    print("")
    print("+++")
    print(section)
    index = section.start.end

    while index < len(template):
        print("--- " + str(index))

        end_tag = get_end_tag(template, index)
        print("End tag: " + str(end_tag))

        # We have a closing tag.
        if end_tag:
            start_tag = get_start_tag(template, index)
            print("Start tag: " + str(start_tag))

            # We have a start tag.
            if start_tag:
                # Is this end tag before the next start?
                if end_tag.start < start_tag.end:
                    # Then close this section.
                    section.end = end_tag
                    section.template(template)
                    return section
                else:
                    # No, then this is nested. Time to go deeper.
                    new = Section(start_tag)
                    # Will add to the end
                    new = again(template, new)
                    index = new.end.end
                    section.add(new)
            # No other start tag.
            else:
                # Then close this section.
                section.end = end_tag
                section.template(template)
                return section
        # Ńo closing tag.
        else:
            # Nothing to do then.
            return section
