import calendar

import pandas as pd


DATE_COLUMN = "Date"
PRICE_COLUMN = "Price"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class DayWisePatternServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, PRICE_COLUMN],
        )
    except Exception as exc:
        raise DayWisePatternServiceError(
            "Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, PRICE_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise DayWisePatternServiceError(
            "Dataset is missing required columns for day wise pattern analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )
    frame[PRICE_COLUMN] = pd.to_numeric(
        frame[PRICE_COLUMN], errors="coerce").fillna(0)
    frame = frame.dropna(subset=[DATE_COLUMN])

    return frame


def _map_time_bucket(hour):
    if hour < 12:
        return "morning"
    if hour < 18:
        return "daytime"
    return "evening"


def _build_empty_day(day):
    return {
        "day": int(day),
        "morning": {"sales_count": 0, "sales_amount": 0.0, "intensity": 0.0},
        "daytime": {"sales_count": 0, "sales_amount": 0.0, "intensity": 0.0},
        "evening": {"sales_count": 0, "sales_amount": 0.0, "intensity": 0.0},
    }


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_day_wise_pattern(dataset_file_path, year, month):
    year = int(year)
    month = int(month)

    frame = _read_dataset_frame(dataset_file_path)
    filtered = frame[
        (frame[DATE_COLUMN].dt.year == year)
        & (frame[DATE_COLUMN].dt.month == month)
    ].copy()

    days_in_month = calendar.monthrange(year, month)[1]
    points_by_day = {day: _build_empty_day(
        day) for day in range(1, days_in_month + 1)}

    if filtered.empty:
        return {
            "days_in_month": days_in_month,
            "total_sales_count": 0,
            "total_sales_amount": 0.0,
            "points": [points_by_day[day] for day in range(1, days_in_month + 1)],
        }

    filtered["bucket"] = filtered[DATE_COLUMN].dt.hour.map(_map_time_bucket)
    filtered["day"] = filtered[DATE_COLUMN].dt.day

    grouped = (
        # count of sale rows and summed sales amount
        filtered.groupby(["day", "bucket"])
        .agg(sales_count=(PRICE_COLUMN, "size"), sales_amount=(PRICE_COLUMN, "sum"))
        .reset_index()
    )

    max_bucket_amount = float(
        grouped["sales_amount"].max()) if not grouped.empty else 0.0

    for _, row in grouped.iterrows():
        day = int(row["day"])
        bucket = str(row["bucket"])
        amount = float(row["sales_amount"])
        count = int(row["sales_count"])
        intensity = 0.0 if max_bucket_amount <= 0 else round(
            (amount / max_bucket_amount) * 100, 2)

        points_by_day[day][bucket] = {
            "sales_count": count,
            "sales_amount": round(amount, 2),
            "intensity": intensity,
        }

    points = [points_by_day[day] for day in range(1, days_in_month + 1)]
    total_sales_count = int(sum(point["morning"]["sales_count"] + point["daytime"]
                            ["sales_count"] + point["evening"]["sales_count"] for point in points))
    total_sales_amount = round(float(sum(point["morning"]["sales_amount"] + point["daytime"]
                               ["sales_amount"] + point["evening"]["sales_amount"] for point in points)), 2)

    return {
        "days_in_month": days_in_month,
        "total_sales_count": total_sales_count,
        "total_sales_amount": total_sales_amount,
        "points": points,
    }
