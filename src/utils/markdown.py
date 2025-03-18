import os
import inspect
import errno
from typing import Any, List


class MarkdownGenerator:
    """
    MarkdownGenerator class: generates the MarkdownGenerator file content.
    """

    def __init__(self) -> None:
        self.content = ""

    def add_header(self, text: str, htype: int = 1) -> "MarkdownGenerator":
        """
        Adds a header block to the content
        :param text: The headers's text
        :param htype: The header type || h1(htype=1), h2(htype=2) etc...
        """
        string = "".join(["#"] * htype) + " {t}".format(t=text)
        self.content += self.create_block(string, 2)
        return self

    def add_text(self, text: str) -> "MarkdownGenerator":
        """
        Adds a text block to the content
        :param text: The text to add
        """
        self.content += self.create_block(text, 2)
        return self

    def add_list_item(self, text: str, depth: int = 0) -> "MarkdownGenerator":
        """
        Adds a list item to the content
        :param text: The list item's text
        :param depth: The intentation depth of the list item
        """
        intent = ""
        if depth > 0:
            intent = "".join([" " * 2] * depth)

        self.content += self.create_block(intent + "- {}".format(text))
        return self

    def add_linebreak(self) -> "MarkdownGenerator":
        """
        Adds a line break block to the content
        """
        self.content += self.create_block("", 1)
        return self

    def add_blockquote(self, *lines: Any) -> "MarkdownGenerator":
        """
        Adds a blockquote to the content
        :param lines: A list of text lines
        """
        _lines: List[str] = list(lines)
        self.content += self.create_block("> " + "  \n".join(_lines), 2)
        return self

    def add_horizontal_rule(self) -> "MarkdownGenerator":
        """
        Adds a horizontal rule block to the content
        """
        self.content += self.create_block("___")
        return self

    def add_code(self, code: str) -> "MarkdownGenerator":
        """
        Adds a code block to the content
        :param code: The codeblock's content
        """
        codeblock = inspect.cleandoc(
            """```code
            {c}
            ```"""
        ).format(c=code.lstrip().rstrip())
        self.content += self.create_block(codeblock, 2)
        return self

    def add_image(self, url: str, alt_text: str) -> "MarkdownGenerator":
        """
        Adds an image to the content
        :param url     : The image url
        :param alt_text: The image alt_text
        """
        self.content += self.create_block("![{}]({})".format(alt_text, url), 2)
        return self

    def add_table(self, rows: List[List[str]]) -> "MarkdownGenerator":
        """
        Adds a table to the content
        :param rows: List of table rows. First one being the header row.
        """

        for i, items in enumerate(list(rows)):
            print(items)
            self.content += "| " + "| ".join(items) + "\n"
            print(self.content)
            if i == 0:
                for item in items:
                    self.content += "| "
                    self.content += "".join(["-"] * len(item))
                self.content += "\n"
        self.content += "\n"
        return self

    @staticmethod
    def link(url: str, text: str = "") -> str:
        """
        Creates a MarkdownGenerator link that can be added in the content
        using the available add_* methods
        ex. markd.add_text(markd.link('https://something.io', 'Get me there!'))
        :param url: The link url
        :param text: Optional text to show

        :return: A MarkdownGenerator link string
        """
        linktext = text if text != "" else url
        return "[{}]({})".format(linktext, url)

    @staticmethod
    def emphasis(text: str) -> str:
        """
        Emphasizes a given text
        ex. markd.add_text(markd.emphasis('This text block will be emphasized'))
        :param text: The text to be emphazised

        :return: An emphazised string
        """
        return "**{}**".format(text)

    @staticmethod
    def italics(text: str) -> str:
        """
        Wraps the given text in asteriscks
        :param text: The text to wrap
        ex. markd.add_text(markd.italics('Like the tower of Pisa!'))
        """
        return "*{}*".format(text)

    @classmethod
    def create_block(cls, text: str = "", lbcount: int = 1) -> str:
        """
        Appends linebreaks to the given text
        :param text: The input text
        :param times: The number of linebreaks that will be appended
        """
        return text + "".join(["\n"] * lbcount)

    def save(self, filename: str) -> None:
        """
        Saves the file
        :param filename: The full path of the destination file
        """
        if not os.path.exists(filename):
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        file = open(filename, "w")
        file.write(self.content)
        file.close()
