import html
import re


class Tag:
    def __init__(self, markup, name, start, end, key=None):
        self.markup = markup
        self.name = name
        self.start = start
        self.end = end
        self.key = key

    def __str__(self):
        s = "Tag: "
        s += repr(self.markup)
        s += " ("
        s += str(self.start)
        s += ", "
        s += str(self.end)
        s += ")"
        return s


class Block:
    def __init__(self, start):
        self.start_tag = start
        self.end_tag = None
        self.else_tag = None

        self.children = []

    def __str__(self):
        s = self.__class__.__name__
        s += " ("
        s += "start_tag=" + str(self.start_tag)
        s += ", end_tag=" + str(self.end_tag)
        s += ", else_tag=" + str(self.else_tag)
        s += ", children=" + str(len(self.children))
        s += ")"
        return s

    def pretty_print(self, level):
        tabs = "\t" * level
        print(tabs + str(self))
        for child in self.children:
            child.pretty_print(level+1)

    def append_child(self, child):
        self.children.append(child)

    def parts(self, template):
        if self.else_tag:
            self.part_inner = template[self.start_tag.end:self.else_tag.start]
            self.part_else = template[self.else_tag.end:self.end_tag.start]
        else:
            self.part_inner = template[self.start_tag.end:self.end_tag.start]

        self.part_outer = template[self.start_tag.start:self.end_tag.end]

    def parse_variables(self, template, data):
        # None escaped.
        matches = re.finditer("{{{(.*?)}}}", template)
        for match in matches:
            tag = match.group(0)
            key = match.group(1)
            value = data if key == "this" else data[key]

            template = template.replace(tag, str(value), 1)

        # Escaped.
        matches = re.finditer("{{([^#/!@].*?)}}", template)
        for match in matches:
            tag = match.group(0)
            key = match.group(1)
            value = data if key == "this" else data[key]

            value = html.escape(str(value))
            template = template.replace(tag, str(value), 1)

        return template


class EachBlock(Block):

    def parse_item(self, template, data, index, key):
        part = self.part_inner
        for child in self.children:
            combined = child.combine(template, data)
            part = part.replace(child.part_outer, combined, 1)

        part = part.replace("{{@index}}", str(index))
        part = part.replace("{{@key}}", str(key))
        return self.parse_variables(part, data)

    def combine(self, template, data):
        result = ""
        key = self.start_tag.key

        try:
            items = data[key]
        except KeyError:
            items = None

        if items and len(items) > 0:
            dictionaries = ["dict", "OrderedDict"]
            if items.__class__.__name__ in dictionaries:
                for index, key in enumerate(items, start=1):
                    item = items[key]
                    result += self.parse_item(template, item, index, key)
            else:
                for index, item in enumerate(items, start=1):
                    result += self.parse_item(template, item, index, key)
        else:
            if self.else_tag:
                result = self.part_else

        return result


class WithBlock(Block):

    def combine(self, template, data):
        # The most outer Section is faked as html instead of a proper
        # "each" tag. Which means it has no real loop but instead really is a
        # flat strucutre that requires special treatment. In the future
        # this should be changed to a more generic solution probably through
        # the "with" functionality.
        if self.start_tag.markup == "html":
            result = template

            for child in self.children:
                combined = child.combine(template, data)
                result = result.replace(child.part_outer, combined, 1)

            return self.parse_variables(result, data)
        else:
            result = ""

            try:
                item = data[self.start_tag.key]
            except KeyError:
                item = None

            if item:
                for child in self.children:
                    combined = child.combine(template, item)
                    result = result.replace(child.part_outer, combined, 1)

                part = self.part_inner
                for child in self.children:
                    combined = child.combine(template, item)
                    part = part.replace(child.part_outer, combined, 1)

                result = self.parse_variables(part, item)
            else:
                if self.else_tag:
                    result = self.part_else

            return result


class IfBlock(Block):

    def combine(self, template, data):
        result = ""
        try:
            item = data[self.start_tag.key]
        except KeyError:
            item = None

        if item:
            part = self.part_inner
            for child in self.children:
                combined = child.combine(template, item)
                part = part.replace(child.part_outer, combined, 1)

            result += self.parse_variables(part, data)
        else:
            if self.else_tag:
                result = self.part_else

        return result


class UnlessBlock(Block):

    def combine(self, template, data):
        result = ""
        try:
            item = data[self.start_tag.key]
        except KeyError:
            item = None

        if not item:
            part = self.part_inner
            for child in self.children:
                combined = child.combine(template, item)
                part = part.replace(child.part_outer, combined, 1)

            result += self.parse_variables(part, data)
        else:
            if self.else_tag:
                result = self.part_else

        return result
