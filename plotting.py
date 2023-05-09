import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session

from alchemy.models import Node

# everything here is rubbish


def plot_text_lengths_density(session: Session, output_file: str):
    # Query all the nodes from the database
    nodes = session.query(Node).all()

    # Calculate the lengths of the text for each node
    # text_lengths = [len(node.text) for node in nodes]

    print("Printing nodes with word count > 4000")
    word_counts = []
    for node in nodes:
        word_count = len(node.text.split())
        if word_count < 1000:
            word_counts.append(word_count)
        # if word_count > 4000:
        #     print(node.document.url)

    # word_counts = [len(node.text.split()) for node in nodes]

    # Create the density plot using seaborn
    sns.set(style="whitegrid")
    sns.kdeplot(word_counts, bw_adjust=0.05)

    # Set plot labels and title
    plt.xlabel("Word Count")
    plt.ylabel("Density")
    plt.title("Density Plot of Wourd Counts in Nodes")

    # Save the plot to a file
    plt.savefig(output_file, dpi=300, bbox_inches="tight")

    # Clear the current figure to prevent overlapping plots when the function is called multiple times
    plt.clf()
