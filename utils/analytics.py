import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_plagiarism_chart(scores):

    plt.figure()

    plt.hist(scores)

    plt.xlabel("Plagiarism Score")
    plt.ylabel("Documents")

    plt.title("Plagiarism Distribution")

    path = "static/charts/plagiarism_chart.png"

    plt.savefig(path)
    plt.close()

    return path