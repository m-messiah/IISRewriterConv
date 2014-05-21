#!/usr/bin/env python3
"""
    Script for converting Intelligencia.rewriter rules (ASPNet urlrewriter)
    to IIS URL Rewrite 2.0 rules
"""
__author__ = 'm_messiah'

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
from sys import stdin, argv
from re import sub, search


class IISRewrite(object):
    """
        Class for converting Intelligencia.rewriter rules (ASPNet urlrewriter)
        to IIS URL Rewrite 2.0 rules
    """
    def __init__(self):
        tree = etree.parse(stdin)
        root = tree.getroot()
        self.rules = [(c.tag, c.attrib, c) for c in root]
        self.new_rules = etree.Element("rules")
        self.fails = []
        self.convert()
        self.write()

    def create_rule(self, name, attr):
        """
            Convert single rule
        """
        new_rule = etree.SubElement(self.new_rules, "rule",
                                    attrib={"name": attr["url"],
                                            "stopProcessing": "true"})
        param = search(r"\\\?(.*)$", attr["url"])
        if param:
            param = param.group(1)
            url = attr["url"][:attr["url"].rfind("?") - 1]
        else:
            url = attr["url"]
        etree.SubElement(new_rule, "match",
                         attrib={"url": url[0] + url[2:]
                                        if url[1] == "/"
                                        else url})
        if param:
            condition = etree.SubElement(new_rule, "conditions")
            etree.SubElement(condition, "add",
                             attrib={"input": "{QUERY_STRING}",
                                     "pattern": param})
        attributes = {"type": name.capitalize(),
                      "url": sub(r"\$(\d)",
                                 r"{C:\g<1>}" if param else r"{R:\g<1>}",
                                 attr["to"])}
        if param:
            attributes["appendQueryString"] = "false"
        etree.SubElement(new_rule, "action", attrib=attributes)

    def convert(self):
        """
            Convert all rules from source
        """
        for name, attr, rule in self.rules:
            if name in ("rewrite", "redirect"):
                self.create_rule(name, attr)
            else:
                self.fails.append(
                    repr(etree.Comment(etree.tounicode(rule).strip()))
                )

    def write(self):
        """
            Print converted rules
        """
        print(etree.tounicode(self.new_rules, pretty_print=True))
        print("<!-- Failed convert. Please, handle it manually-->\n")
        print("\n".join(self.fails))


if __name__ == "__main__":
    if len(argv) > 1:
        print("Converter from IIS URLRewriter2 config xml to "
              "standard IIS >7 Rewriter.\n"
              "Conditions and other rules must be handled manually.")
        exit(1)
    IISRewrite()
