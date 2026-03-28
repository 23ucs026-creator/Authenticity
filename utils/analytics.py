import os
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_plagiarism_chart(scores):
    # Ensure charts directory exists
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    plt.figure()

    plt.hist(scores)

    plt.xlabel("Plagiarism Score")
    plt.ylabel("Documents")

    plt.title("Plagiarism Distribution")

    path = os.path.join(charts_dir, "plagiarism_chart.png")

    plt.savefig(path)
    plt.close()

    return path