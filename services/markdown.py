import re
import textwrap

from services.markdown_example import markdown_text


def parse_markdown(document, title="Heading 0"):
    # Regular expressions for detecting headings and content
    regex = re.compile(r"^(#+)\s(.*)$", re.MULTILINE)

    # Find the headings and their levels
    headings = regex.findall(document)

    # Initialize the root node
    root_node = {
        "title": title,
        "content": document.strip(),
        "length": len(document.strip()),
        "level": 0,
        "children": [],
        "breadcrumbs": title,
    }

    # Function to add a node to the hierarchy
    def add_node(parent, node):
        if not parent["children"]:
            parent["children"].append(node)
        else:
            last_child = parent["children"][-1]
            if last_child["level"] < node["level"]:
                add_node(last_child, node)
            else:
                parent["children"].append(node)

    def get_subtree_content(document, start_index, end_index):
        return document[start_index:end_index].strip()

    # Add nodes to the hierarchy
    for index, heading in enumerate(headings):
        level = len(heading[0])
        title = heading[1]

        # Find the content of the heading
        start_index = document.find(heading[0] + " " + title)
        if index + 1 < len(headings):
            end_index = document.find(
                "\n" + headings[index + 1][0] + " ", start_index + 1
            )
        else:
            end_index = len(document)

        content = get_subtree_content(document, start_index, end_index)

        node = {
            "title": title,
            "content": content,
            "length": len(content),
            "level": level,
            "children": [],
            "breadcrumbs": "",
        }

        add_node(root_node, node)

    return root_node


# Maximum length of content in a node
MAX_CONTENT_LENGTH = 1000
OVERLAP_LENGTH = 100


def split_long_content(content, level, breadcrumbs, overlap=OVERLAP_LENGTH):
    wrapper = textwrap.TextWrapper(
        width=MAX_CONTENT_LENGTH - overlap, break_long_words=False
    )
    wrapped_content = wrapper.wrap(content)

    chunks = []
    start = 0
    end = MAX_CONTENT_LENGTH

    for i, chunk in enumerate(wrapped_content):
        if i == 0:
            chunks.append(chunk)
            end = start + len(chunk)
        else:
            end = start + len(chunk) + overlap
            chunks.append(content[start:end])

        start = end - overlap

    nodes = []
    for idx, chunk in enumerate(chunks):
        # Don't include the last breadcrumb for the first part
        content_breadcrumbs = (
            ">".join(breadcrumbs.split(">"))
            if idx > 0
            else ">".join(breadcrumbs.split(">")[:-1])
        )
        content = f"{content_breadcrumbs}\n{chunk}"
        node = {
            "title": f"Part {idx + 1}",
            "content": content,
            "length": len(chunk) + len(content_breadcrumbs),
            "level": level,
            "children": [],
            "breadcrumbs": breadcrumbs + f" > Part {idx + 1}",
        }
        nodes.append(node)

    return nodes


# def split_long_content(content, level, breadcrumbs):
#     chunks = [
#         content[i : i + MAX_CONTENT_LENGTH]
#         for i in range(0, len(content), MAX_CONTENT_LENGTH)
#     ]
#     nodes = []
#     for idx, chunk in enumerate(chunks):
#         node = {
#             "title": f"Part {idx + 1}",
#             "content": chunk,
#             "length": len(chunk),
#             "level": level,
#             "children": [],
#             "breadcrumbs": breadcrumbs + f" > Part {idx + 1}",
#         }
#         nodes.append(node)
#     return nodes


def add_breadcrumbs(node, breadcrumbs):
    node["breadcrumbs"] = breadcrumbs
    node["content"] = f"{node['breadcrumbs']}\n{node['content']}"
    node["length"] = len(node["content"])


def update_content(node, breadcrumbs):
    if not node["children"]:
        # add_breadcrumbs(node, breadcrumbs)

        if node["length"] > MAX_CONTENT_LENGTH:
            node["children"] = split_long_content(
                node["content"], node["level"] + 1, breadcrumbs + " > " + node["title"]
            )

        add_breadcrumbs(node, breadcrumbs)

        return node["content"]
    else:
        child_contents = "\n\n".join(
            update_content(child, breadcrumbs + " > " + node["title"])
            for child in node["children"]
        )
        node["content"] = f"{node['content']}\n\n{child_contents}"
        node["length"] = len(node["content"])
        return node["content"]


# def update_content(node, breadcrumbs):
#     if not node["children"]:
#         node["breadcrumbs"] = breadcrumbs
#         node["content"] = f"{node['breadcrumbs']}\n{node['content']}"
#         node["length"] = len(node["content"])
#         return node["content"]
#     else:
#         child_contents = "\n\n".join(
#             update_content(child, breadcrumbs + " > " + node["title"])
#             for child in node["children"]
#         )
#         node["content"] = f"{node['content']}\n\n{child_contents}"
#         node["length"] = len(node["content"])
#         return node["content"]


# Parse the document
document_node = parse_markdown(markdown_text)

# Update each child node with the full subtree text
for child_node in document_node["children"]:
    update_content(child_node, document_node["title"])

print(document_node)

from helpers import pretty_print_dict

pretty_print_dict(document_node)
