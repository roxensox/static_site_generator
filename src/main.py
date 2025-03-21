from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
import re, os, shutil


project = os.path.dirname(os.path.abspath(__name__))
public = os.path.join(project, "public")
static = os.path.join(project, "static")


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

def copy_contents(src, dest, depth):
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


if __name__ == "__main__":
    copy_contents(static, public, 0)
