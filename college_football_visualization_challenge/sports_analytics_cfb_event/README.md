# College Football Visualization Challenge

A casual, one-hour data competition for mixed experience levels. Participants
use a guided Google Colab notebook to explore college-football play-by-play and
make one visualization that communicates a finding.

## What's in this folder

- `collect_data.py` downloads one completed season and makes a small, readable
  CSV for the event.
- `starter.ipynb` guides participants through opening the data, learning what
  its columns mean, building a chart, and changing the chart to answer their own
  question.
- `requirements.txt` lists the packages needed to prepare the CSV locally.
- `data/college_football_plays_2025.csv` is created when you run the data script.

## Downloading the Data

1. On a computer with Python, install the data-preparation packages and create
   the CSV:

   ```bash
   python -m pip install -r requirements.txt
   python collect_data.py
   ```

   The default is the completed 2025 season. You can use another season with,
   for example, `python collect_data.py --season 2024 --output data/college_football_plays_2024.csv`.
   If you change the season, update the notebook's `DATA_URL` to the matching
   CSV name after you push the data file to GitHub.

Colab link:

```text
https://colab.research.google.com/github/alliemcd/SAA_football/blob/main/starter.ipynb
```


## Dataset notes

The CSV has one row per offensive play from scrimmage. The collector uses the
public SportsDataverse ESPN college-football play-by-play Parquet release, then
keeps only the columns needed for the notebook. The source has many more
columns; this activity file intentionally keeps the first steps approachable.

| Column | Meaning |
| --- | --- |
| `season`, `week`, `game_id` | Where and when the play happened. |
| `offense_team`, `defense_team` | Teams involved in the play. |
| `quarter` | Quarter in which the play began. |
| `play_type` | Run, pass, or other scrimmage play. |
| `down`, `yards_to_go` | Down number and distance needed for a first down. |
| `yards_gained` | Yardage recorded for the play. |
| `epa` | Expected points added: a model-based estimate of how the play changed the offense's scoring expectation. Positive usually means the play improved it; negative usually means it hurt it. |
| `successful` | Whether the play had positive EPA in the source model. |
| `score_difference_at_start` | Offense's score minus defense's score before the play. |

Play-by-play data can have missing values or source corrections. The notebook
keeps the competition focused on visual exploration rather than treating the
file as a perfect official record. Cite SportsDataverse and ESPN as the data
source when you share work made with the data.

## Source and attribution

- SportsDataverse college-football play-by-play release:
  <https://github.com/sportsdataverse/sportsdataverse-data/releases/tag/espn_cfb_pbp>
- Dataset column guide:
  <https://github.com/sportsdataverse/cfbfastR-cfb-data/blob/main/DATASETS.md>

The provided notebook and collection script are for this student event. The
underlying data are maintained by their source; check the source's current
terms and attribution guidance before redistributing or using them beyond the
event.
