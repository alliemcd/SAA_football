"""Download and prepare one season of college-football play-by-play data.

Data source: SportsDataverse's public ESPN college-football play-by-play release.
The script downloads one season, keeps the small set of columns used in the
event notebook, and writes a friendly CSV into data/.

Examples
--------
    python collect_data.py
    python collect_data.py --season 2024
    python collect_data.py --season 2025 --output data/football_plays.csv

The data source requires no API key. A completed season is recommended so that
the dataset will not change while people are using it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

import pandas as pd
import requests


DATA_URL = (
    "https://github.com/sportsdataverse/sportsdataverse-data/releases/download/"
    "espn_cfb_pbp/play_by_play_{season}.parquet"
)

# These are the source columns that the notebook uses. Keeping the selection
# small makes the event CSV much easier for beginners to look at.
SOURCE_COLUMNS = [
    "season",
    "week",
    "game_id",
    "start.pos_team.name",
    "start.def_pos_team.name",
    "period",
    "rush",
    "pass",
    "scrimmage_play",
    "start.down",
    "start.distance",
    "statYardage",
    "EPA",
    "EPA_success",
    "start.pos_score_diff",
]


def download_parquet(url: str, destination: Path) -> None:
    """Download a file with a clear error if the public release is unavailable."""
    try:
        with requests.get(url, stream=True, timeout=(20, 180)) as response:
            response.raise_for_status()
            with destination.open("wb") as output:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        output.write(chunk)
    except requests.RequestException as error:
        raise RuntimeError(
            "The play-by-play file could not be downloaded. Check your internet "
            "connection and the season number, then try again. Source URL: " + url
        ) from error


def prepare_data(season: int, output_path: Path) -> pd.DataFrame:
    """Download, simplify, and save the selected season's scrimmage plays."""
    url = DATA_URL.format(season=season)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Store the large source file in a temporary location instead of adding it
    # to the event repository. The compact CSV is the file participants use.
    with tempfile.TemporaryDirectory() as temporary_folder:
        parquet_path = Path(temporary_folder) / f"play_by_play_{season}.parquet"
        print(f"Downloading the {season} play-by-play file...")
        download_parquet(url, parquet_path)

        try:
            plays = pd.read_parquet(parquet_path, columns=SOURCE_COLUMNS)
        except ImportError as error:
            raise RuntimeError(
                "Reading Parquet files needs pyarrow. Install the packages with "
                "`python -m pip install -r requirements.txt`."
            ) from error
        except (ValueError, OSError) as error:
            raise RuntimeError(
                "The downloaded file could not be read. The source may have "
                "changed; check the SportsDataverse release and its data dictionary."
            ) from error

    # Use only offensive plays from scrimmage. This leaves out kickoffs, punts,
    # and other special-teams events, which are a distraction for this activity.
    plays = plays.loc[plays["scrimmage_play"].fillna(False)].copy()
    plays = plays.dropna(subset=["start.pos_team.name", "start.def_pos_team.name"])

    # Make the source's compact/technical column names easier to understand.
    plays["play_type"] = "Other"
    plays.loc[plays["rush"].fillna(False), "play_type"] = "Run"
    plays.loc[plays["pass"].fillna(False), "play_type"] = "Pass"

    plays = plays.rename(
        columns={
            "start.pos_team.name": "offense_team",
            "start.def_pos_team.name": "defense_team",
            "period": "quarter",
            "start.down": "down",
            "start.distance": "yards_to_go",
            "statYardage": "yards_gained",
            "EPA": "epa",
            "EPA_success": "successful",
            "start.pos_score_diff": "score_difference_at_start",
        }
    )

    columns_for_notebook = [
        "season",
        "week",
        "game_id",
        "offense_team",
        "defense_team",
        "quarter",
        "play_type",
        "down",
        "yards_to_go",
        "yards_gained",
        "epa",
        "successful",
        "score_difference_at_start",
    ]
    plays = plays[columns_for_notebook].sort_values(
        ["week", "game_id", "quarter"], na_position="last"
    )

    # Give the output CSV consistent simple values and keep the missing values
    # as blank cells; pandas reads them back as missing data automatically.
    plays.to_csv(output_path, index=False)
    print(f"Saved {len(plays):,} plays to {output_path}")
    print(f"Columns: {', '.join(plays.columns)}")
    return plays


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--season",
        type=int,
        default=2025,
        help="season year to download (default: 2025)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="where to save the prepared CSV (defaults to data/college_football_plays_SEASON.csv)",
    )
    arguments = parser.parse_args()

    if not 2004 <= arguments.season <= 2100:
        parser.error("Choose a season from 2004 onward.")

    output_path = arguments.output or Path(
        f"data/college_football_plays_{arguments.season}.csv"
    )

    try:
        prepare_data(arguments.season, output_path)
    except RuntimeError as error:
        print(f"\nCould not prepare the data: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
