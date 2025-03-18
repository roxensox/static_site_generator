from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re


def main():
    test = TextNode("hello, world", TextType.BOLD)
    print(test)


def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text, props={"href":text_node.url})
        case TextType.IMAGE:
            return LeafNode(tag="img", props={"src":text_node.url, "alt":text_node.text})
        case _:
            raise TypeError()


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    next_special = False
    search_term = f"{delimiter}[^{delimiter}]*{delimiter}"
    for node in old_nodes:
        matches = re.findall(search_term, node.text)
        remaining_text = re.sub(search_term, "|;&", node.text)
        match_num = 0
        for i, term in enumerate(remaining_text.split("|;&")):
            if i == 0 and term == "":
                new_nodes.append(TextNode(re.sub(delimiter, "", matches[match_num]), text_type))
                match_num += 1
            else:
                if term == "":
                    continue
                new_nodes.append(TextNode(term, TextType.TEXT))
                if match_num < len(matches):
                    new_nodes.append(TextNode(re.sub(delimiter, "", matches[match_num]), text_type))
                    match_num += 1

    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\]]*)\]\(([^\)]*)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text):
    pattern = r"\[([^\]]*)\]\(([^\)]*)\)"
    return re.findall(pattern, text)


if __name__ == "__main__":
    print(extract_markdown_links("[lmao](this is a url) first and then [kek](this is a second url)"))
