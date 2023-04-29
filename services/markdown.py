# import re

# from termcolor import colored

# markdown_text = """We use [CodeCov](https://codecov.io/) to monitor changes to our test coverage. There is a handy browser extension to view coverage gutters directly in GitHub.

# 1) You'll need to use Chrome

# 2) Install the [Sourcegraph Chrome extension](https://chrome.google.com/webstore/detail/sourcegraph/dgjhfomjieaadpoljlnidmbgkdffpack?hl=en)

# 3) Enable the [CodeCov extension](https://sourcegraph.com/extensions/sourcegraph/codecov) on Sourcegraph

# 4) Click the burger bar at the top of the Sano GitHub repository

# ![Screen_Recording_2020-05-19_at_11.06.02.mov](441e009b_Screen_Recording_2020-05-19_at_11.06.02.mov.gif)

# 5) Enter your API key from CodeCov

# <br/>

# You should now be able to view coverage gutters:

# <br/>

# ![Untitled.mov](a96dcf5d_Untitled.mov.gif)

# []()

# <br/>

# """


# def parse_markdown(document):
#     # Regular expressions for detecting headings and content
#     section_regex = re.compile(r"^##\s(.*)$", re.MULTILINE)
#     subsection_regex = re.compile(r"^###\s(.*)$", re.MULTILINE)

#     # Find the sections
#     sections = section_regex.split(document)[1:]

#     # Organize sections into a dictionary
#     parsed_sections = []

#     for i in range(0, len(sections), 2):
#         title = sections[i]
#         content = sections[i + 1]

#         # Find the subsections
#         subsections = subsection_regex.split(content)[1:]

#         parsed_subsections = []

#         for j in range(0, len(subsections), 2):
#             sub_title = subsections[j]
#             sub_content = subsections[j + 1]

#             parsed_subsections.append(
#                 {"title": sub_title, "content": sub_content.strip()}
#             )

#         parsed_sections.append(
#             {
#                 "title": title,
#                 "content": content.strip(),
#                 "subsections": parsed_subsections,
#             }
#         )

#     return parsed_sections


# def test_parse_markdown():
#     print(markdown_text)

#     print("parsing markdown")

#     # Parse the document
#     sections = parse_markdown(markdown_text)

#     # Print the parsed sections
#     for section in sections:
#         print(colored(f"Section: {section['title']}", "green"))
#         for subsection in section["subsections"]:
#             print(colored(f"   Subsection: {subsection['title']}", "red"))
#             print(f"      Content: {subsection['content']}")
#         print("\n")


import re

markdown_text = """
Note we initially started working in this Notion location: [https://www.notion.so/sanogenetics/Implement-Study-Survey-versioning-3603755460d5465b9b1c3f06b0936e23](https://www.notion.so/sanogenetics/Implement-Study-Survey-versioning-3603755460d5465b9b1c3f06b0936e23)

# 📄Portal Documentation:

[//]: # (child_page is not supported)

Portal Participant Documentation [[The Flowsel](/d53b54c66fb34d60acba89c743785ce8)] 

<br/>

# 🕰Planning and discussions:

[//]: # (child_page is not supported)

[//]: # (child_page is not supported)

[//]: # (child_page is not supported)
"""


def parse_markdown(document):
    # Regular expressions for detecting headings and content
    heading_regex = re.compile(r"^(#+)\s(.*)$", re.MULTILINE)

    # Find the headings and their levels
    headings = heading_regex.findall(document)

    # Initialize the root node
    root_node = {
        "title": "Document",
        "content": document.strip(),
        "level": 0,
        "children": [],
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
            "level": level,
            "children": [],
        }

        add_node(root_node, node)

    return root_node


def print_node(node, indent=0):
    print("  " * indent + f"Level {node['level']} {node['title']}")
    print("  " * (indent + 1) + f"Content: {node['content']}")
    print()
    if node["children"]:
        for child in node["children"]:
            print_node(child, indent + 1)


# def get_full_content(node):
#     if not node["children"]:
#         return node["content"]
#     else:
#         child_contents = "\n\n".join(
#             get_full_content(child) for child in node["children"]
#         )
#         return f"{node['content']}\n\n{child_contents}"


def update_content(node):
    if not node["children"]:
        return node["content"]
    else:
        child_contents = "\n\n".join(
            update_content(child) for child in node["children"]
        )
        node["content"] = f"{node['content']}\n\n{child_contents}"
        return node["content"]


# Parse the document
document_node = parse_markdown(markdown_text)

# Update each child node with the full subtree text
for child_node in document_node["children"]:
    update_content(child_node)

print(document_node)


from helpers import pretty_print_dict

pretty_print_dict(document_node)
