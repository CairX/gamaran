import re
from tags import Tag, EachBlock, WithBlock


def new_block(start_tag):
    if start_tag.name == "each":
        return EachBlock(start_tag)
    elif start_tag.name == "with":
        return WithBlock(start_tag)
    else:
        return None


def get_start_tag(end_tag, template, index):
    pattern = "{{#(" + end_tag.name + ") (.*?)}}"
    search = re.search(pattern, template[index:])

    if search:
        markup = search.group(0)
        name = search.group(1)
        key = search.group(2)

        span = search.span(0)
        start = index + span[0]
        end = index + span[1]

        return Tag(markup, name, start, end, key)
    else:
        return None


def get_end_tag(template, index):
    search = re.search("{{/(each|with)}}", template[index:])

    if search:
        markup = search.group(0)
        name = search.group(1)

        span = search.span(0)
        start = index + span[0]
        end = index + span[1]

        return Tag(markup, name, start, end)
    else:
        return None


def get_else_tag(template, start, end):
    markup = "{{else}}"
    tag_start = template.find(markup, start, end)

    if tag_start == -1:
        return None
    else:
        tag_end = tag_start + len(markup)
        tag = template[tag_start:tag_end]

        return Tag(tag, "else", tag_start, tag_end)


def parse(template, section):
    index = section.start_tag.end

    while index < len(template):
        end_tag = get_end_tag(template, index)

        # We have a closing tag.
        if end_tag:
            start_tag = get_start_tag(end_tag, template, index)

            # We have a start tag.
            if start_tag:
                # Is this end tag before the next start?
                if end_tag.start < start_tag.end:
                    # Then close this section.
                    section.end_tag = end_tag
                    section.else_tag = get_else_tag(template, start_tag.end, end_tag.start)
                    # When end has been added calculate parts from template.
                    section.parts(template)
                    return section
                # No, then this is nested. Time to go deeper.
                else:
                    new = new_block(start_tag)
                    # Will add to the end
                    new = parse(template, new)
                    index = new.end_tag.end
                    section.append_child(new)
            # No other start tag.
            else:
                # Then close this section.
                section.end_tag = end_tag
                section.else_tag = get_else_tag(template, section.start_tag.end, end_tag.start)
                # When end has been added calculate parts from template.
                section.parts(template)
                return section
        # Ńo closing tag.
        else:
            # Nothing to do then.
            return section
