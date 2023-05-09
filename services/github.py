from github import Github

g = Github("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")

# Specify the repository and the pull request number
repo_name = 'sanogenetics/sano'
# pr_number = 6969

# Get the pull request
repo = g.get_repo(repo_name)
# pr = repo.get_pull(pr_number)

# print(pr.diff_url)

subfolder = "server"


lengths = []
def get_child_python_files(node):
    global lengths
    contents = repo.get_contents(node)

    for node in contents:
        # print(node.path)

        # If the node is a Python file
        if node.type == "file" and node.path.endswith(".py"):
            # print("Python file")
            print(node.path)
            file_contents = node.decoded_content.decode("utf-8")
            if len(file_contents.split())>1000:
                print("Long file")
                sections = file_contents.split("\n\n\n")
                [print(len(section.split())) for section in sections]
            lengths.append(len(node.decoded_content.decode("utf-8")))

        # If the node is a directory and its name doesn't start with a period
        elif node.type == "dir" and not node.path.split("/")[-1].startswith("."):
            # print("Directory")
            # print(node.path)
            get_child_python_files(str(node.path))  # Recursive call


get_child_python_files("server")

with open("lengths.txt", "w") as f:
    f.write(str(lengths))




# for node in contents:
#     print(node.name)
#     # if not node.path.startswith("."):
#     #     print(node.)