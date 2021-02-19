from collections import defaultdict
from itertools import cycle
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


if __name__ == "__main__":
    data = pd.read_csv("data.csv", index_col="person")
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 21))

    # Remove redirected pages.
    data = data.drop(
        [
            "Arthur Nixon",
            "Christopher Morcom",
            "Harold Nixon",
            "David Jacob Eisenhower",
            "Frank Woodrow O'Flaherty",
            "Eutímio Guerra",
            "Vladimir Spiridonovich Putin",
            "Benjamin Holcomb",
            "Benjamin Harrison Holcomb",
            "Sadayoshi Tanabe",
            "Jean Finnegan Biden",
            "Travis Maldonado",
            "Neva Morris",
            "Gianna Bryant",
        ]
    )

    deaths = data.loc[data.groupby("year")["views"].idxmax()]
    # Occupations.
    occupations = pd.read_csv("occupations.csv", index_col="person")
    # Merge people and their occupations.
    deaths = deaths.join(occupations["field"], on="person")
    # Count number of each occupation for use in the legend.
    occupation_counts = deaths.groupby(["field"])["field"].agg(["count"])

    # Convert views to millions.
    deaths.views /= 1e6

    # Axis label font sizes.
    ax.tick_params(axis="both", which="major", labelsize=10)

    # Plot total views.
    sns.set_color_codes("pastel")
    bplot = sns.barplot(x="views", y="year", data=deaths, color="b", orient="h")

    # Add names.
    padding = max(deaths.views) / 100
    for person, p in zip(deaths.index, bplot.patches):
        x = p.get_x() + p.get_width() + padding
        y = p.get_y() + p.get_height() - 0.15
        ax.text(x, y, person, ha="left", size=8)

    # Set bar colours depending on occupation.
    cycler = cycle(sns.color_palette("colorblind"))
    category_colours = defaultdict(lambda: next(cycler))
    # Ensure category colours follow alphabetical order.
    categories = sorted([str(field) for field in deaths["field"].unique()])
    categories.remove("other")
    for category in categories:
        category_colours[category]
    categories.append("other")
    category_colours["other"] = "#555"
    for bar, field in zip(ax.patches, deaths["field"]):
        bar.set_color(category_colours[field])

    # Legend.
    legend_patches = [
        Patch(
            color=category_colours[category],
            label=f"{category} ({occupation_counts.at[category, 'count']})",
        )
        for category in category_colours
    ]
    ax.legend(handles=legend_patches, loc="upper right", frameon=True, fontsize="small")

    # Show only decades in full.
    years = []
    for year in deaths.year:
        stryear = str(year)
        if year % 10 != 0:
            stryear = stryear[2:]
        years.append(stryear)
    ax.set_yticklabels(years)
    ax.set(
        title="Most viewed people articles on Wikipedia by year of death",
        xlim=(0, 35),
        xlabel="Pageviews in 2020 (million)",
        ylabel="Year",
    )
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("deaths.pdf")
    plt.savefig("deaths.png", dpi=150)