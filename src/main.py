from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from config import *
import split_block
import re, os, shutil, pathlib, sys


def rm_r(folder: str) -> None:
    '''
    Recursively deletes a folder (emulates rm -r on Unix)

    Inputs:
        folder: A string containing the target path

    Outputs:
        None
    '''
    # Fetches the contents of the folder
    items = os.listdir(folder)
    # Checks if the folder contains anything
    if len(items) > 0:
        # Makes a path string from the item
        item_path = os.path.join(folder, items[0])
        # Removes the item if it's a file
        if os.path.isfile(item_path):
            os.remove(item_path)
        # Recursively deletes the item if it's a folder
        else:
            rm_r(item_path)
        # Recurses until the folder is empty
        rm_r(folder)
    else:
        # Deletes the main folder and returns
        os.rmdir(folder)
        return


def copy_contents(src: str, dest: str, depth=0) -> None:
    '''
    Copies the contents of one folder to another, by deleting and recreating the destination folder

    Inputs:
        src: A path-string of the folder you want to copy
        dest: A path-string of the folder you want to copy to
        depth: The recursion depth (defaults to 0; any user wouldn't need to modify this)

    Outputs:
        None
    '''
    # Removes the folder if recursion depth is 0
    if depth < 1:
        if os.path.exists(dest):
            rm_r(dest)
        os.mkdir(dest)

    # Gathers the items in the source folder if they aren't already in the destination folder
    src_items = os.listdir(src)
    dest_items = os.listdir(dest)
    copy_items = [i for i in src_items if i not in dest_items]

    # If there are any items to copy, continues, otherwise returns
    if len(copy_items) > 0:
        item = copy_items[0]
    else:
        return

    # Sets the item and destination paths
    item_path = os.path.join(src, item)
    dest_path = os.path.join(dest, item)

    # Copies the item if it's a file, otherwise recursively copies the folder
    if os.path.isfile(item_path):
        shutil.copy(item_path, dest_path)
    else:
        os.mkdir(dest_path)
        copy_contents(item_path, dest_path, 1)
    # Recurses until there's nothing left to copy
    copy_contents(src, dest, 1)


def extract_title(markdown: str) -> str:
    '''
    Pulls the title line from a markdown string

    Inputs:
        markdown: A string of markdown

    Outputs:
        A string of the title without the markdown notation
    '''
    lines = markdown.split("\n")
    # Checks for the title line using regex
    title = [line for line in lines if re.match("^# .*", line) != None]
    if title == []:
        raise Exception("Markdown must have a title")
    else:
        title = title[0]
        return re.sub("^# ", "", title)


def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str) -> None:
    '''
    Generates a page of html at a specified destination folder given a path to a markdown file

    Inputs:
        from_path: A path-string to the markdown file
        template_path: A path-string to the html template
        dest_path: A path-string to the file you want to make
        basepath: The program's root directory

    Outputs:
        None
    '''
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as md, open(template_path, "r") as template, open(dest_path, "w") as output:
        md = md.read()
        template = template.read()
        # Gets the title from the markdown file
        title = extract_title(md)
        # Gets the node built from markdown_to_html_node
        html_node = split_block.markdown_to_html_node(md)
        # Outputs the node to a string of html
        html_node = html_node.to_html()
        # Modifies the template using regex
        out = template
        out = re.sub("{{ Title }}", title, out)
        out = re.sub("{{ Content }}", html_node, out)
        # This part ensures that the resource paths are correct for deployment
        out = re.sub('href="/', f'href="{basepath}', out)
        out = re.sub('src="/', f'src="{basepath}', out)
        output.write(out)


def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str) -> None:
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
            generate_pages_recursive(contents, TEMPLATE, dest_dir_path, basepath)
        # Otherwise, copies the file over
        else:
            # If the item is a markdown file, this generates the html page while copying
            if item.suffix == ".md":
                dest_dir_path = re.sub(".md$", ".html", dest_dir_path)
                generate_page(item, TEMPLATE, dest_dir_path, basepath)
            # Otherwise, just copies it over
            else:
                shutil.copy(item, dest_dir_path)
    # Removes the finished item from the list and recurses
    generate_pages_recursive(dir_path_content[1:], template_path, dest_dir_path, basepath)


def main():
    # Sets the basepath to the first argument when this program is called
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    # Copies the static folder to the docs folder
    copy_contents(STATIC, DOCS)
    # Builds the path to the content folder
    content = os.path.join(PROJECT, "content")
    # Gets a list of the contents of the content folder
    initial_contents = [i for i in pathlib.Path(content).iterdir()]
    # Passes those contents to generate_pages_recursive to start it off
    generate_pages_recursive(initial_contents, TEMPLATE, DOCS, basepath)


if __name__ == "__main__":
    main()
