#!/usr/bin/python3
__author__ = 'm_messiah'

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
import sys
from re import sub


class IISRewrite(object):
    def __init__(self, source="rewriter.xml", output="new_rewriter.xml"):
        tree = etree.parse(source)
        root = tree.getroot()
        self.rules = [(c.tag, c.attrib, c) for c in root]
        self.new_rules = etree.Element("rules")
        self.fails = []
        self.convert()
        self.write(output)

    def create_rule(self, name, attr):
        new_rule = etree.SubElement(self.new_rules, "rule",
                                    attrib={"name": name,
                                            "stopProcessing": "true"})
        etree.SubElement(new_rule, "match",
                         attrib={"url": attr["url"][0] + attr["url"][2:]
                                 if attr["url"][1] == "/" else attr["url"]})
        attributes = {"type": name,
                      "url": sub(r"\$(\d)", "{R:\g<1>}", attr["to"])}
        if name == "redirect":
            attributes["redirectType"] = "Found"
        etree.SubElement(new_rule, "action", attrib=attributes)

    def convert(self):
        for name, attr, rule in self.rules:
            if name in ("rewrite", "redirect"):
                self.create_rule(name, attr)
            else:
                self.fails.append(
                    repr(etree.Comment(etree.tounicode(rule).strip()))
                )

    def write(self, output):
        with open(output, "w", encoding='utf-8') as out:
            out.write("<rewrite>\n")
            out.write(etree.tounicode(self.new_rules, pretty_print=True))
            out.write("<!-- Failed convert. Please, handle it manually-->\n")
            out.write("\n".join(self.fails))
            out.write("</rewrite>")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Using: python3 ./IISRewriterConv.py "
              "<source_file> <output_file>"
              "-------------------------------------\n"
              "Converter from IIS URLRewriter2 config xml to "
              "standard IIS >7 Rewriter.\n"
              "Now handle only <rewrite /> and <redirect /> rules.\n"
              "Conditions and other rules must be handled manually.")
        exit(1)
    IISRewriter = IISRewrite(sys.argv[1], sys.argv[2])
    print("Successfully converted to {}".format(sys.argv[2]))
