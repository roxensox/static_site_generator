from block import BlockType
import re
import math

def markdown_to_blocks(markdown):
    markdown_blocks = markdown.split("\n\n")
    for i in range(0, len(markdown_blocks)):
        markdown_blocks[i] = markdown_blocks[i].strip()
    return [i for i in markdown_blocks if i != ""]


def block_to_block_type(block):
    if len(re.findall("^#{1,6} .*", block)) > 0:
        return BlockType.HEADING
    elif len(re.findall("^`{3}[^`]*`{3}$", block)) > 0:
        return BlockType.CODE

    lines = block.split("\n")
    quote_pattern = "^>"
    ul_pattern = "^- "
    ol_pattern = "^[1-9]*. "

    if math.prod([re.search(quote_pattern, i) != None for i in lines]):
        return BlockType.QUOTE
    elif math.prod([re.search(ul_pattern, i) != None for i in lines]):
        return BlockType.UNORDERED_LIST
    elif math.prod([re.match(ol_pattern, i) != None for i in lines]):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.NORMAL




if __name__ == "__main__":
    md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line







- This is a list
- with items
"""
    print(markdown_to_blocks(md))
