# Most viewed people articles on Wikipedia by year of death

For a bit of fun, I calculated and plotted the most viewed people articles on
Wikipedia by year of death. In other words, the most "popular" death in each of
the past 122 years.

Results are shown on the [releases
page](https://github.com/SeanDS/wikipedia-deaths/releases/tag/1.0.0). An
extended writeup is shown on [my
blog](https://attackllama.com/2021/02/most-viewed-people-articles-wikipedia-year-of-death).

## Requirements
Python 3 (probably 3.6+), Wikipedia-API, Pandas, Seaborn (`pip install
seaborn`). Install these with e.g. `pip install wikipediaapi pandas seaborn`.
The `requests` package is also needed but this gets installed by Wikipedia-API.

## Usage
Edit `download.py` and find the line where the header for the requests to the
Wikipedia API is set. Uncomment the `User-Agent` field and set it to something
unique (the API will block requests without this header).

Run `download.sh` or `download.py` from Python. Wait many hours. Once finished,
run `convertdata.py` then `plotbar.py`.

## Notes
### Network problems
Use `download.sh` (if on Linux) to re-run the download script if it exits with a
non-zero code. This is used to handle cases where requests to Wikipedia's API
time out. The downloaded data is cached for every 100 people.

### 404s when downloading certain pages
Expected behaviour for when a page has had 0 views in the specified time period.
See the [pageview API
docs](https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews#Gotchas).

### Occupations
These are defined in `occupations.csv` and are entirely subjective. I guessed
from scanning the headings of each person's Wikipedia article in cases where I
didn't know the person.

## Credits
Sean Leavey  
https://attackllama.com/