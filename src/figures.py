from venv import create
import numpy as np
from pathlib import Path
from argparse import ArgumentParser
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.image import AxesImage
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import seaborn as sb
from scipy.cluster.hierarchy import linkage, leaves_list
from tempfile import mkstemp
import os
from src.mosaic import arrange_four, arrange_two_to_height, WrappedSvgImage
import matplotlib.ticker as mticker


def make_pyramid(op_df: pd.DataFrame, country_name: str):
    ages = list(np.arange(19, 91, 1))

    fig, ax = plt.subplots(1, 1, figsize=(8, 8)) # type: ignore

    age_labels = np.array([str(a) for a in ages[1:]])

    op_df = op_df.copy()
    op_df["bracket"] = pd.cut(op_df["age_years"], bins=ages, right=False, labels=age_labels.tolist()) # type: ignore
    
    stuff = op_df.groupby(["bracket", "sex"]).size().unstack(fill_value=0).reindex(age_labels, fill_value=0)
    ax.barh(age_labels, -stuff["male"], color="#009fd4", label="Male")
    ax.barh(age_labels, stuff["female"], color="#f64747", label="Female")

    ax.set_title(country_name, fontsize=18)
    ax.set_xlabel("Count", fontsize=18)
    ax.set_ylabel("Age", fontsize=18)

    size = max(stuff["male"].max(), stuff["female"].max()) * 1.05
    ax.set_xlim(-size, size)
    ax.yaxis.set_ticks(age_labels[np.arange(0, len(age_labels), 2)])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, pos: v + 19))
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, pos: abs(v)))
    ax.tick_params(axis="both", labelsize=13)

    ax.legend(prop={'size': 13})
    return fig


def plot_heatmap(ax: Axes, df: np.ndarray, cmap, vmin: float) -> AxesImage:
    ax.set_aspect('auto')
    # viridis = mpl.colormaps['viridis'].resampled(8) # type: ignore

    # cmap = ListedColormap(["blue", "green", "#05F41D", "yellow"])
    # cmap = ListedColormap(viridis(np.linspace(0, 1, 5)))
    # cmap= None

    # comparisons = df[np.triu_indices_from(df, k=1)]
    # mean = np.mean(comparisons) - np.std(comparisons) * 3
    # vmin = np.min(comparisons)

    ax.set_xticks([])
    ax.set_yticks([])

    ax.invert_yaxis()

    return ax.pcolormesh(df, cmap=cmap, vmin=vmin, vmax=100, rasterized=True) #type: ignore


def add_colorbar(max: Axes, ax: Axes, mesh):
    cb = ax.figure.colorbar(mesh, ax=max, cax=ax, use_gridspec=True)

    pos = ax.get_position()
    new_height = pos.height * 0.5
    new_bottom = pos.y0 + (pos.height - new_height) / 2

    # ax.set_position([pos.x0, new_bottom, pos.width, new_height])
    ax.set_aspect(10)
    cb.ax.tick_params(axis="both", labelsize=18)

    cb.set_label("ANI%", rotation=270, labelpad=16, fontsize=20)


def plot_histo(ax: Axes, df, bin_count: int) -> None:
    # bins, edges = np.histogram(df.to_numpy() * 100, bins=bin_count)
    # ax.bar(edges[:-1], bins)
    ax.hist(df, bin_count)
    # ax.hist(df.to_numpy() * 100, bin_count, edgecolor="black")
    # ax.set_yscale("log")
    ax.set_xlabel("ANI%", fontsize=20, labelpad=16)
    ax.set_ylabel("Count of comparisons", fontsize=20, labelpad=16)
    ax.tick_params(axis="both", labelsize=16)


def plot_clustermap(parent_fig: Figure, df: np.ndarray, vmin: float):
    # cond_matrix = squareform(100 - df)
    avrg = linkage(df, method="average", optimal_ordering=True)

    leaves = leaves_list(avrg)

    sorted_df = df[leaves, :][:, leaves]

    viridis = mpl.colormaps['viridis'].resampled(8) # type: ignore
    cmap = ListedColormap(viridis(np.linspace(0, 1, 5)))

    ax = parent_fig.subplots(nrows=2, ncols=2, width_ratios=(0.8, 0.05), height_ratios=(0.2, 0.8), gridspec_kw={"wspace": 0, "hspace": 0}) #type: ignore

    mesh = plot_heatmap(ax[1][0], sorted_df, cmap, vmin)
    add_colorbar(ax[1][0], ax[1][1], mesh)
    sb.matrix.dendrogram(sorted_df, linkage=avrg, ax=ax[0][0], label=False) #type: ignore

    ax[0][0].set_axis_off()
    ax[0][1].set_axis_off()
    ax[1][0].set_axis_off()
    # ax[1][1].set_axis_off()

    # parent_fig.tight_layout()

    # sb.clustermap(df, col_linkage=avrg, row_linkage=avrg, row_cluster=True, **hmap_dict)
    return parent_fig



def create_clustermap_histo_panel(out_name: str, matrix: np.ndarray, vmin: float):
    histo_fig: Figure | None = None

    fig = plt.figure(figsize=(10, 11.5), layout='constrained')
    fig.set_dpi(300)

    plot_clustermap(fig, matrix, vmin)

    _, cluster_path = mkstemp(suffix=".svg")
    _, histo_path = mkstemp(suffix=".svg")

    try:
        fig.savefig(Path(cluster_path))

        histo_fig = plt.figure(figsize=(10, 10), layout='constrained')
        histo_fig.set_dpi(300)

        plot_histo(histo_fig.add_subplot(), matrix[np.triu_indices(matrix.shape[0], k=1)], 128)

        histo_fig.savefig(Path(histo_path))

        arrange_two_to_height(out_name, WrappedSvgImage(Path(cluster_path)), WrappedSvgImage(Path(histo_path)), spacing=4)
    finally:
        plt.close(fig)
        if histo_fig is not None:
            plt.close(histo_fig)

        os.remove(cluster_path)
        os.remove(histo_path)


def create_four_clustermaps_panel(out_name: Path, matrices: list[np.ndarray], titles: list[str], vmin: float):
    temp_files = []
    figs = []

    try:
        for matrix, title in zip(matrices, titles):
            fig = plt.figure(figsize=(10, 11.5), layout='constrained')
            fig.set_dpi(300)

            fig.suptitle(f"{title} (n = {matrix.shape[0]})", fontsize=20)

            figs.append(fig)

            plot_clustermap(fig, matrix, vmin)

            dest_path = Path(mkstemp(suffix=".svg")[1])
            fig.savefig(dest_path)

            temp_files.append(dest_path)

        arrange_four(
            str(out_name),
            tuple(WrappedSvgImage(a) for a in temp_files), #type: ignore
            spacing=4)
    finally:
        for fig in figs:
            plt.close(fig)
    
        for temp_file in temp_files:
            os.remove(temp_file)


def create_pyramid_panel(out_panel_path: Path, sample: pd.DataFrame, country_ordering: list[str]):
    figures: list[tuple[str, Figure]] = []

    try:
        geo_groups = sample.groupby("geographic_location")

        for country in country_ordering:
            geo_group = geo_groups.get_group(country)

            fig = make_pyramid(geo_group, country)

            dest_path = mkstemp(".svg")[1]

            figures.append((dest_path, fig))
            fig.savefig(dest_path)


        fig = make_pyramid(sample, "Pooled")

        dest_path = mkstemp(".svg")[1]
        
        figures.append((dest_path, fig))
        fig.savefig(dest_path)

        arrange_four(
            str(out_panel_path),
            tuple(WrappedSvgImage(path) for path, _ in figures), #type: ignore
            4)


    finally:
        for temp_file, figure in figures:
            os.remove(temp_file)
            plt.close(figure)
