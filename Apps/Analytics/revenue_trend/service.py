import calendar

import pandas as pd


DATE_COLUMN = "Date"
PRICE_COLUMN = "Price"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class RevenueTrendServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, PRICE_COLUMN],
        )
    except Exception as exc:
        raise RevenueTrendServiceError("Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, PRICE_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise RevenueTrendServiceError(
            "Dataset is missing required columns for revenue trend analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )
    frame[PRICE_COLUMN] = pd.to_numeric(
        frame[PRICE_COLUMN], errors="coerce").fillna(0)

    return frame.dropna(subset=[DATE_COLUMN])


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_revenue_trend(dataset_file_path, year, month=None):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]

    if month is None:
        grouped = (
            filtered.groupby(filtered[DATE_COLUMN].dt.month)[PRICE_COLUMN]
            .sum()
            .reindex(range(1, 13), fill_value=0)
        )
        labels = [calendar.month_abbr[month_index]
                  for month_index in range(1, 13)]
        granularity = "month"
    else:
        month = int(month)
        filtered = filtered[filtered[DATE_COLUMN].dt.month == month]
        day_count = calendar.monthrange(int(year), month)[1]
        grouped = (
            filtered.groupby(filtered[DATE_COLUMN].dt.day)[PRICE_COLUMN]
            .sum()
            .reindex(range(1, day_count + 1), fill_value=0)
        )
        labels = [str(day) for day in range(1, day_count + 1)]
        granularity = "day"

    points = []
    for idx, label in enumerate(labels, start=1):
        revenue = float(grouped.loc[idx]) if idx in grouped.index else 0.0
        points.append(
            {
                "label": label,
                "revenue": round(revenue, 2),
            }
        )

    total_revenue = round(float(sum(point["revenue"] for point in points)), 2)

    return {
        "granularity": granularity,
        "total_revenue": total_revenue,
        "points": points,
    }
