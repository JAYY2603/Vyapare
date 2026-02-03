from collections import Counter
from itertools import combinations

import pandas as pd


DATE_COLUMN = "Date"
ORDER_ID_COLUMN = "OrderID"
ITEM_COLUMN = "Item"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"
MAX_BAR_POINTS = 20


class MarketBasketAnalysisServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, ORDER_ID_COLUMN, ITEM_COLUMN],
        )
    except Exception as exc:
        raise MarketBasketAnalysisServiceError(
            "Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, ORDER_ID_COLUMN, ITEM_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise MarketBasketAnalysisServiceError(
            "Dataset is missing required columns for market basket analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )

    frame[ORDER_ID_COLUMN] = frame[ORDER_ID_COLUMN].astype(str).str.strip()
    frame[ITEM_COLUMN] = frame[ITEM_COLUMN].astype(str).str.strip()

    frame = frame.dropna(subset=[DATE_COLUMN])
    frame = frame[(frame[ORDER_ID_COLUMN] != "") & (frame[ITEM_COLUMN] != "")]

    return frame


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_frequently_bought_together(dataset_file_path, year):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]
    if filtered.empty:
        return {
            "total_pair_occurrences": 0,
            "points": [],
        }

    pair_counter = Counter()

    grouped_orders = filtered.groupby(ORDER_ID_COLUMN)[ITEM_COLUMN]
    for _, item_series in grouped_orders:
        unique_items = sorted(set(item_series.tolist()))
        if len(unique_items) < 2:
            continue

        for pair in combinations(unique_items, 2):
            pair_counter[pair] += 1

    if not pair_counter:
        return {
            "total_pair_occurrences": 0,
            "points": [],
        }

    sorted_pairs = pair_counter.most_common(MAX_BAR_POINTS)
    points = [
        {
            "label": f"{item_a} + {item_b}",
            "count": int(count),
        }
        for (item_a, item_b), count in sorted_pairs
    ]

    total_pair_occurrences = int(sum(pair_counter.values()))

    return {
        "total_pair_occurrences": total_pair_occurrences,
        "points": points,
    }
