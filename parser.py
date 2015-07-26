import re


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

    def pretty_print(self, level):
        tabs = "\t" * level
        print(tabs + str(self))
        for s in self.sections:
            s.printSections(level+1)

    def add(self, section):
        self.sections.append(section)

    def parts(self, template):
        self.part_inner = template[self.start.end:self.end.start]
        self.part_outer = template[self.start.start:self.end.end]

    def combine(self, template, data):
        # The most outer Section is faked as html instead of a proper
        # "each" tag. Which means it has no real loop but instead really is a
        # flat strucutre that requires special treatment. In the future
        # this should be changed to a more generic solution probably through
        # the "with" functionality.
        if self.start.tag == "html":
            result = template

            for section in self.sections:
                combined = section.combine(template, data)
                result = result.replace(section.part_outer, combined, 1)

            return variables(data, result)

        # This is the proper "each" tag logic.
        else:
            result = ""
            items = data[self.start.key]

            for item in items:
                part = self.part_inner
                for section in self.sections:
                    combined = section.combine(template, item)
                    part = part.replace(section.part_outer, combined, 1)

                result += variables(item, part)

            return result


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


def get_end_tag(template, index):
    tag_start = template.find(each_tag_end, index)

    if tag_start == -1:
        return None
    else:
        tag_end = tag_start + len(each_tag_end)
        tag = template[tag_start:tag_end]

        return Tag(tag, tag_start, tag_end)


def parse(template, section):
    index = section.start.end

    while index < len(template):
        end_tag = get_end_tag(template, index)

        # We have a closing tag.
        if end_tag:
            start_tag = get_start_tag(template, index)

            # We have a start tag.
            if start_tag:
                # Is this end tag before the next start?
                if end_tag.start < start_tag.end:
                    # Then close this section.
                    section.end = end_tag
                    # When end has been added calculate parts from template.
                    section.parts(template)
                    return section
                else:
                    # No, then this is nested. Time to go deeper.
                    new = Section(start_tag)
                    # Will add to the end
                    new = parse(template, new)
                    index = new.end.end
                    section.add(new)
            # No other start tag.
            else:
                # Then close this section.
                section.end = end_tag
                # When end has been added calculate parts from template.
                section.parts(template)
                return section
        # Ńo closing tag.
        else:
            # Nothing to do then.
            return section
