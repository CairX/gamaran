import re
from tags import Tag, EachBlock, WithBlock


def parse(template, data):
    # Initiate with a global with-block that contains everything.
    start_tag = Tag("html", "html", 0, 0)
    end_tag = Tag("html", "html", len(template), len(template))
    block = WithBlock(start_tag)
    block.end_tag = end_tag

    template = remove_dashed_comments(template)
    template = remove_simple_comments(template)

    block = parse_blocks(template, block)
    result = block.combine(template, data)

    return result


def remove_dashed_comments(template):
    pattern = "{{!--.*?--}}"

    comments = re.findall("[\n][ \t]*" + pattern, template, re.DOTALL)
    for comment in comments:
        template = template.replace(comment, "", 1)

    comments = re.findall(pattern, template, re.DOTALL)
    for comment in comments:
        template = template.replace(comment, "", 1)

    return template


def remove_simple_comments(template):
    pattern = "{{!.*?}}"

    comments = re.findall("[\n][ \t]*" + pattern, template, re.DOTALL)
    for comment in comments:
        template = template.replace(comment, "", 1)

    comments = re.findall(pattern, template, re.DOTALL)
    for comment in comments:
        template = template.replace(comment, "", 1)

    return template


def parse_blocks(template, block):
    index = block.start_tag.end

    while index < len(template):
        end_tag = get_end_tag(template, index)

        # We have a closing tag.
        if end_tag:
            start_tag = get_start_tag(end_tag, template, index)

            # We have a start tag.
            if start_tag:
                # Is this end tag before the next start?
                if end_tag.start < start_tag.end:
                    # Then close this block.
                    block.end_tag = end_tag
                    block.else_tag = get_else_tag(template, start_tag.end, end_tag.start)
                    # When end has been added calculate parts from template.
                    block.parts(template)
                    return block
                # No, then this is nested. Time to go deeper.
                else:
                    new = new_block(start_tag)
                    # Will add to the end
                    new = parse_blocks(template, new)
                    index = new.end_tag.end
                    block.append_child(new)
            # No other start tag.
            else:
                # Then close this block.
                block.end_tag = end_tag
                block.else_tag = get_else_tag(template, block.start_tag.end, end_tag.start)
                # When end has been added calculate parts from template.
                block.parts(template)
                return block
        # Ńo closing tag.
        else:
            # Nothing to do then.
            return block


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
