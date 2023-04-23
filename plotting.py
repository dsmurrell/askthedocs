import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy.orm import Session

from alchemy.models import Section


def plot_text_lengths_density(session: Session, output_file: str):
    # Query all the sections from the database
    sections = session.query(Section).all()

    # Calculate the lengths of the text for each section
    # text_lengths = [len(section.text) for section in sections]

    word_counts = [len(section.text.split()) for section in sections]

    # Create the density plot using seaborn
    sns.set(style="whitegrid")
    sns.kdeplot(word_counts, bw_adjust=0.05)

    # Set plot labels and title
    plt.xlabel("Word Count")
    plt.ylabel("Density")
    plt.title("Density Plot of Wourd Counts in Sections")

    # Save the plot to a file
    plt.savefig(output_file, dpi=300, bbox_inches="tight")

    # Clear the current figure to prevent overlapping plots when the function is called multiple times
    plt.clf()
