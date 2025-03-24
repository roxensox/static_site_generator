from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    '''
    Turns a TextNode object into an HTMLNode object

    Inputs:
        text_node: A TextNode object

    Outputs:
        An HTMLNode object with the appropriate tag
    '''
    # Builds the node according to the TextType label on the TextNode
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)
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


def split_nodes_delimiter(old_nodes: list, delimiter: str, text_type: TextType) -> list:
    '''
    Splits a list of TextNode objects into smaller nodes based on a specified delimiter

    Inputs:
        old_nodes: A list of TextNodes to be analyzed and split further
        delimiter: A string with the delimiter you want to divide the TextNodes based on
        text_type: A TextType enum to assign to the nodes split off using the delimiter

    Outputs:
        A list of new nodes split using the delimiter
    '''
    new_nodes = []
    # A boolean that indicates whether the next node is special in order to alternate properly
    next_special = False
    # A regex built using the delimiter
    search_term = f"{delimiter}[^{delimiter}]*{delimiter}"
    # Loops through the old nodes
    for node in old_nodes:
        # It's hard to handle nested nodes, so this skips anything that isn't vanilla text
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        # Gathers the portions of the text that match the regex
        matches = re.findall(search_term, node.text)
        # If there is no match, this adds the node back to the list as a regular text node
        if len(matches) == 0:
            new_nodes.append(node)
            continue
        # Captures the text that isn't a match and adds a delimiter that's unlikely to appear naturally
        remaining_text = re.sub(search_term, "|;&", node.text)
        match_num = 0
        # Splits the text by the new delimiter and enumerates through the segments
        for i, term in enumerate(remaining_text.split("|;&")):
            # If it starts with a blank, we know a match was there, so we start the alternation here
            if i == 0 and term == "":
                new_nodes.append(TextNode(re.sub(delimiter, "", matches[match_num]), text_type))
                match_num += 1
            else:
                # Since the alternating pattern takes care of the remaining matches, we can safely ignore blanks that aren't at the beginning
                if term == "":
                    continue
                # Adds a regular text node
                new_nodes.append(TextNode(term, TextType.TEXT))
                # If there are remaining matches, they get added to the output list
                if match_num < len(matches):
                    new_nodes.append(TextNode(re.sub(delimiter, "", matches[match_num]), text_type))
                    match_num += 1
    return new_nodes


def extract_markdown_images(text: str) -> list:
    '''
    Extracts images from a string of markdown

    Inputs:
        text: A string of markdown to search

    Outputs:
        A list of strings that match the image regex
    '''
    # Matches text in the form ![example](example.url)
    pattern = r"!\[([^\]]*)\]\(([^\)]*)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text: str) -> list:
    '''
    Extracts links from a string of markdown

    Inputs:
        text: A string of markdown to search

    Outputs:
        A list of strings that match the link regex
    '''
    # Matches text in the form [example](example.url)
    pattern = r"(?<!!)\[([^\]]*)\]\(([^\)]*)\)"
    return re.findall(pattern, text)


def split_nodes_image(old_nodes: list) -> list:
    '''
    Splits images from a node into image nodes

    Inputs:
        old_nodes: A list of nodes to be split

    Outputs:
        A new list of nodes containing the image nodes
    '''
    # Regex to match the ![image](url) pattern
    pattern = r"!\[[^\]]*\]\([^\)]*\)"
    new_nodes = []
    # Loops through the nodes
    for node in old_nodes:
        # Ignores non-text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        # Gets the list of images found in the node
        imgs = extract_markdown_images(node.text)
        # Returns the input if there are none
        if len(imgs) == 0:
            return old_nodes
        # Splits the remaining text and enumerates through it (see split_nodes_delimiter for more thorough documentation)
        remaining_text = re.sub(pattern, "|;&", node.text)
        match_num = 0
        for i, term in enumerate(remaining_text.split("|;&")):
            if i == 0 and term == "":
                new_nodes.append(TextNode(imgs[match_num][0], TextType.IMAGE, imgs[match_num][1]))
                match_num += 1
            else:
                if term == "":
                    continue
                new_nodes.append(TextNode(term, TextType.TEXT))
                if match_num < len(imgs):
                    new_nodes.append(TextNode(imgs[match_num][0], TextType.IMAGE, imgs[match_num][1]))
                    match_num += 1
    return new_nodes


def split_nodes_link(old_nodes: list) -> list:
    '''
    Splits links from a node into link nodes

    Inputs:
        old_nodes: A list of nodes to be split

    Outputs:
        A new list of nodes containing the link nodes
    '''
    # See split_nodes_image for more thorough documentation
    pattern = r"(?<!!)\[[^\]]*\]\([^\)]*\)"
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            return old_nodes
        remaining_text = re.sub(pattern, "|;&", node.text)
        match_num = 0
        for i, term in enumerate(remaining_text.split("|;&")):
            if i == 0 and term == "":
                new_nodes.append(TextNode(links[match_num][0], TextType.LINK, links[match_num][1]))
                match_num += 1
            else:
                if term == "":
                    continue
                new_nodes.append(TextNode(term, TextType.TEXT))
                if match_num < len(links):
                    new_nodes.append(TextNode(links[match_num][0], TextType.LINK, links[match_num][1]))
                    match_num += 1
    return new_nodes


def text_to_text_nodes(text: str) -> list:
    '''
    Takes a string of markdown text and turns it into text node(s)

    Inputs:
        text: A string of markdown text

    Outputs:
        A list of nodes generated from the text
    '''
    check = False
    out_nodes = [TextNode(text, TextType.TEXT)]
    out_nodes = split_nodes_image(out_nodes)
    out_nodes = split_nodes_link(out_nodes)
    out_nodes = split_nodes_delimiter(out_nodes, r"\*\*", TextType.BOLD)
    out_nodes = split_nodes_delimiter(out_nodes, "_", TextType.ITALIC)
    out_nodes = split_nodes_delimiter(out_nodes, "`", TextType.CODE)
    return out_nodes

