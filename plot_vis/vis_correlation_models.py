from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sn
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA

from plot_vis.vis_transfer_learning import load_results
from utils import model_names_short, color_scheme


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, model.distances_,
                                      counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


if __name__ == '__main__':
    result_id = 230
    idx_prototypes_bar_plot = 1

    dataset = "ImageNet"

    figsize = 5

    result_data, config = load_results(Path(f"../results/{result_id}"))
    # correlations, significance, features, dim_reduced_features,
    correlations = result_data["correlations"]
    features = result_data["features"]
    dim_reduced_features = result_data["dim_reducted_features"]

    # # UMAP
    # x_umap = dim_reduced_features['umap']
    # y_short = [model_names_short[name] for name in dim_reduced_features['labels']]
    # colors = [color_scheme[name] for name in dim_reduced_features['labels']]
    # plt.figure(figsize=(figsize, figsize))
    # plt.scatter(x_umap[:, 0], x_umap[:, 1], c=colors)
    # for xc, yc, t in zip(x_umap[:, 0], x_umap[:, 1], y_short):
    #     plt.text(xc, yc, t)
    # # plt.title("UMAP of RDMs")
    # plt.tight_layout(.5)
    # plt.savefig(f"results/{result_id}/umap_rdms.eps", format="eps")
    # plt.show()

    # # tSNE
    X_tsne = dim_reduced_features['tsne']
    y_short = [model_names_short[name] for name in dim_reduced_features['labels']]
    colors = [color_scheme[name] for name in dim_reduced_features['labels']]

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(1.5 * figsize, 0.8 * figsize))
    ax = axes[1]
    ax.scatter(X_tsne[:, 0], X_tsne[:, 1], c=colors)
    for xc, yc, t in zip(X_tsne[:, 0], X_tsne[:, 1], y_short):
        ax.text(xc, yc, t, ha='center')
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_aspect((x1 - x0) / (y1 - y0))
    ax.set_title("(b)")
    # plt.title("t-SNE of RDMs")

    y, X = zip(*features.items())
    y_short = [model_names_short[name] for name in y]
    colors = [color_scheme[name] for name in y]
    X = np.stack(X, axis=0)

    # Dendrogram
    ax = axes[0]
    model = AgglomerativeClustering(distance_threshold=0, n_clusters=None, affinity="correlation", linkage="average")
    model = model.fit(X)
    # plt.title("Dendrogram of hierarchical clustering of RDMs. Average linkage.")
    plot_dendrogram(model, labels=y_short, leaf_rotation="vertical", ax=ax)
    ax.set_title("(a)")
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    ax.set_aspect((x1 - x0) / (y1 - y0))
    plt.tight_layout(pad=1)
    plt.savefig(f"results/{result_id}/tsne_dendrogram_hierarchical_clustering_rdms_3.svg", format="svg")
    plt.show()

    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    plt.figure(figsize=(figsize, figsize))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=colors)
    for xc, yc, t in zip(X_pca[:, 0], X_pca[:, 1], y_short):
        plt.text(xc, yc, t)
    # plt.title("PCA of RDMs")
    # plt.xlabel("1st component")
    # plt.ylabel("2nd component")
    plt.tight_layout(.5)
    plt.savefig(f"results/{result_id}/pca_rdms.eps", format="eps")
    plt.show()


    figsize = 10

    mat = np.zeros((len(correlations), len(correlations)))
    # pval = np.zeros((len(significance), len(significance)))
    labels = []

    # Correlation between models
    for i, (model_1, corrs) in enumerate(sorted(correlations.items())):
        labels.append(model_names_short[model_1])
        for j, (model_2, corr) in enumerate(sorted(corrs.items())):
            mat[i, j] = corr
            # pval = significance[model_1][model_2]

    plt.figure(figsize=(figsize, figsize))
    sn.heatmap(mat, annot=True, xticklabels=labels, yticklabels=labels)
    # plt.title("Pearson correlations between RDMs of vision and text models.")
    plt.tight_layout(pad=.5)
    plt.savefig(f"results/{result_id}/plot_corr.eps", format="eps")
    plt.show()

    # plt.figure(figsize=(figsize, figsize))
    # sn.heatmap(pval, annot=True, xticklabels=labels, yticklabels=labels)
    # # plt.title("Pearson correlations between RDMs of vision and text models.")
    # plt.tight_layout(.5)
    # plt.savefig(f"results/{result_id}/plot_pval.eps", format="eps")
    # plt.show()