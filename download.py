import sys
import logging
from pathlib import Path
from collections import defaultdict
import pickle
from datetime import datetime
import wikipediaapi
import requests

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.INFO)
STREAM_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(STREAM_HANDLER)


def removeprefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]

def read_cache(cache):
    if cache.is_file():
        LOGGER.info(f"Loading cache at {cache}")
        with cache.open("rb") as fobj:
            return pickle.load(fobj)
    

def write_cache(cache, data):
    LOGGER.info(f"Caching data to {cache}")
    with cache.open("wb") as fobj:
        pickle.dump(data, fobj)


if __name__ == "__main__":
    START_YEAR = 1900
    STOP_YEAR = 2020
    PAGEVIEW_START = "20200101"
    PAGEVIEW_STOP = "20210101"

    uuid = f"{START_YEAR}-{STOP_YEAR}-{PAGEVIEW_START}-{PAGEVIEW_STOP}".casefold()
    data_cache = Path.cwd() / f"cache-{uuid}.pickle"
    log_file = Path.cwd() / f"log-{uuid}"

    log_file_handler = logging.FileHandler(log_file)
    log_file_handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(log_file_handler)

    LOGGER.debug(f"\n--- run at {datetime.now()} ---\n")

    excluded_prefices = ["Category:", "Deaths in", "List of"]
    wiki = wikipediaapi.Wikipedia("en")
    data = read_cache(data_cache)

    if data is None:
        data = {"years": defaultdict(dict)}

    if "category" not in data:
        deaths = wiki.page("Category:Deaths_by_year")
        data["category"] = deaths

    write_cache(data_cache, data)

    cache_counter = 0
    
    try:
        for year in range(START_YEAR, STOP_YEAR+1):
            category_name = f"Category:{year} deaths"
            category_page = data["category"].categorymembers[category_name]
            
            ntotal = len(category_page.categorymembers)
            for ncurrent, (member_name, member) in enumerate(category_page.categorymembers.items(), start=1):
                if member_name in data["years"][year]:
                    # Already downloaded.
                    LOGGER.debug(f"Skipping existing {member_name}")
                    continue

                skip = False
                for prefix in excluded_prefices:
                    if member_name.startswith(prefix):
                        LOGGER.info(f"Skipping {member_name}")
                        skip = True
                        break
                if skip:
                    continue

                LOGGER.info(f"processing {member_name}")

                if not getattr(member, "fullurl"):
                    # Assume page was deleted recently.
                    LOGGER.error(f"Assuming {member_name} page was deleted recently - skipping")
                    continue

                member_slug = removeprefix(member.fullurl, "https://en.wikipedia.org/wiki/")

                try:
                    # Grab pageviews.
                    response = requests.get(
                        (
                            f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
                            f"/en.wikipedia.org/all-access/all-agents/{member_slug}/monthly"
                            f"/{PAGEVIEW_START}/{PAGEVIEW_STOP}"
                        ),
                        # headers={"User-Agent": "***SET-ME***"}
                    )
                    response.raise_for_status()
                except requests.exceptions.HTTPError:
                    LOGGER.exception(f"Assuming {member_name} counts are 0")
                    pageviews = 0
                else:
                    pageviews = sum([month["views"] for month in response.json()["items"]])

                LOGGER.info(f"{year} {ncurrent}/{ntotal}: {member_name} page views = {pageviews}")
                data["years"][year][member_name] = {
                    "slug": member_slug,
                    "views": pageviews
                }
                cache_counter += 1

                if cache_counter % 100 == 0:
                    write_cache(data_cache, data)
                    cache_counter = 0
    except Exception as e:
        LOGGER.exception("Unknown handled error")
        sys.exit(1)
    
    write_cache(data_cache, data)