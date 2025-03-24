from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import split_block
import re, os, shutil, pathlib, sys
from config import PROJECT, PUBLIC, STATIC, TEMPLATE, DOCS

BASEPATH = sys.argv[1] if len(sys.argv) > 1 else "/"

def rm_r(folder):
    items = os.listdir(folder)
    if len(items) > 0:
        item_path = os.path.join(folder, items[0])
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            rm_r(item_path)
            os.rmdir(item_path)
    else:
        return

def copy_contents(src, dest, depth=0):
    if depth <= 1:
        rm_r(dest)

    src_items = os.listdir(src)
    dest_items = os.listdir(dest)
    copy_items = [i for i in src_items if i not in dest_items]

    if len(copy_items) > 0:
        item = copy_items[0]
    else:
        return

    item_path = os.path.join(src, item)
    dest_path = os.path.join(dest, item)

    if os.path.isfile(item_path):
        shutil.copy(item_path, dest_path)
    else:
        os.mkdir(dest_path)
        copy_contents(item_path, dest_path, 2)
    copy_contents(src, dest, 2)


def extract_title(markdown):
    lines = markdown.split("\n")
    title = [line for line in lines if re.match("^# .*", line) != None]
    if title == []:
        raise Exception("Markdown must have a title")
    else:
        title = title[0]
        return re.sub("^# ", "", title)


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as md, open(template_path, "r") as template, open(dest_path, "w") as output:
        md = "".join([i for i in md.readlines()])
        template = "".join([i for i in template.readlines()])
        title = extract_title(md)
        html_node = split_block.markdown_to_html_node(md)
        html_node = html_node.to_html()
        out = template
        out = re.sub("{{ Title }}", title, out)
        out = re.sub("{{ Content }}", html_node, out)
        out = re.sub('href="/', f'href="{BASEPATH}', out)
        out = re.sub('src="/', f'src="{BASEPATH}', out)
        output.write(out)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    '''
    Recursively copies the contents of the content folder to the public folder in HTML form
    '''
    if dir_path_content == []:
        return
    else:
        # Gets the first item in the directory
        item = dir_path_content[0]
        # Uses regex to update the destination path
        dest_dir_path = re.sub("/content/", "/docs/", str(item))
        # Recurses on the item if the item is a directory
        if pathlib.Path(item).is_dir():
            contents = [i for i in pathlib.Path(item).iterdir()]
            if not os.path.exists(dest_dir_path):
                os.mkdir(dest_dir_path)
            generate_pages_recursive(contents, TEMPLATE, dest_dir_path)
        # Otherwise, copies the file over
        else:
            # If the item is a markdown file, this generates the html page while copying
            if item.suffix == ".md":
                dest_dir_path = re.sub(".md$", ".html", dest_dir_path)
                generate_page(item, TEMPLATE, dest_dir_path)
            # Otherwise, just copies it over
            else:
                shutil.copy(item, dest_dir_path)
    # Removes the finished item from the list and recurses
    generate_pages_recursive(dir_path_content[1:], template_path, dest_dir_path)


def main():
    basepath = sys.argv[0] if sys.argv[0] else "/"
    index = os.path.join(PROJECT, "content/index.md")
    destination = os.path.join(DOCS, "index.html")
    content = os.path.join(PROJECT, "content")
    copy_contents(STATIC, DOCS)
    initial_contents = [i for i in pathlib.Path(content).iterdir()]
    generate_pages_recursive(initial_contents, TEMPLATE, DOCS)


if __name__ == "__main__":
    main()
