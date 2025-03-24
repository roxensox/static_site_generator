from block import BlockType
import re
import math
from htmlnode import HTMLNode, ParentNode, LeafNode
from splitter_funcs import text_node_to_html_node, text_to_text_nodes
from config import PROJECT, PUBLIC, STATIC

def markdown_to_blocks(markdown: str) -> list:
    '''
    Turns a string of markdown into blocks of markdown

    Inputs:
        markdown: A string of a full markdown document

    Outputs:
        Each chunk of text divided by two new lines, with spaces removed
    '''
    markdown_blocks = markdown.split("\n\n")
    for i in range(0, len(markdown_blocks)):
        markdown_blocks[i] = markdown_blocks[i].strip()
    return [i for i in markdown_blocks if i != ""]


def block_to_block_type(block: str) -> BlockType:
    '''
    Gets the type of the input block using regular expressions

    Inputs:
        block: A string of markdown text received from markdown_to_blocks

    Returns:
        A BlockType enum instance representing the type of block the input text matches
    '''
    if len(re.findall("^#{1,6} .*", block)) > 0:
        return BlockType.HEADING
    elif len(re.findall("^`{3}[^`]*`{3}$", block)) > 0:
        return BlockType.CODE

    lines = block.split("\n")
    quote_pattern = "^>"
    ul_pattern = "^- "
    ol_pattern = "^[0-9]*. "

    # Uses boolean multiplication to see if there are any lines that break the pattern and therefore disqualify the block for its blocktypes
    if math.prod([re.search(quote_pattern, i) != None for i in lines]):
        return BlockType.QUOTE
    elif math.prod([re.search(ul_pattern, i) != None for i in lines]):
        return BlockType.UNORDERED_LIST
    elif math.prod([re.match(ol_pattern, i) != None for i in lines]):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def line_to_children(line: str) -> list:
    '''
    Splits an input string into a list of HTMLNode objects by first splitting them into TextNodes

    Inputs:
        line: A line of markdown text

    Outputs:
        A list of HTMLNode objects
    '''
    out = [text_node_to_html_node(i) for i in text_to_text_nodes(line)]
    return out


def markdown_to_html_node(markdown: str) -> ParentNode:
    '''
    Takes in a whole markdown document as a string and returns a single HTMLNode object containing everything extracted from the input text

    Inputs:
        markdown: A string containing a whole markdown document

    Outputs:
        An HTMLNode object (ParentNode, really) with child-nodes representing all special text contained within
    '''
    #TODO: Simplify this, there's a lot of redundant logic in this

    # Gets the blocks
    blocks = markdown_to_blocks(markdown)
    # Initializes the output node as a div with an empty list of children
    main_node = ParentNode("div", [])
    # Adds the HTMLNodes made from the blocks into the main node's child list based on their BlockTypes
    for block in blocks:
        match block_to_block_type(block):
            # Each BlockType removes the type indicators used in markdown when transforming to HTMLNode
            case BlockType.CODE:
                main_node.children.append(ParentNode("pre", [LeafNode(tag="code", value=block[4:-4])]))
                continue
            case BlockType.HEADING:
                # First extracts the level of the heading using regex to display properly in html
                heading_level = len(re.match("^#{1,6} ", block)[0][:-1])
                lines = [re.sub("^#{1,6} ", "", i) for i in block.split("\n")]
                for line in lines:
                    main_node.children.append(ParentNode(f"h{heading_level}", line_to_children(line)))
                continue
            case BlockType.UNORDERED_LIST:
                lines = [re.sub("^- ", "", i) for i in block.split("\n")]
                node = ParentNode("ul", [])
                for line in lines:
                    node.children.append(ParentNode("li", line_to_children(line)))
                main_node.children.append(node)
                continue
            case BlockType.ORDERED_LIST:
                lines = [re.sub("^[0-9]*. ", "", i) for i in block.split("\n")]
                node = ParentNode("ol", [])
                for line in lines:
                    node.children.append(ParentNode("li", line_to_children(line)))
                main_node.children.append(node)
                continue
            case BlockType.QUOTE:
                lines = [re.sub("^>", "", i) for i in block.split("\n")]
                lines = [i.strip() for i in lines]
                node = ParentNode("blockquote", [])
                for line in lines:
                    node.children.extend(line_to_children(line))
                    node.children.extend([LeafNode(value="<br>")])
                main_node.children.append(node)
            case BlockType.PARAGRAPH:
                line = " ".join(block.split("\n"))
                node = ParentNode("p", [])
                node.children.extend(line_to_children(line))
                main_node.children.append(node)
    return main_node
