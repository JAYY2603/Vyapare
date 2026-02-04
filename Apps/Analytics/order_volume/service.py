import calendar

import pandas as pd


DATE_COLUMN = "Date"
ORDER_ID_COLUMN = "OrderID"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class OrderVolumeServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, ORDER_ID_COLUMN],
        )
    except Exception as exc:
        raise OrderVolumeServiceError("Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, ORDER_ID_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise OrderVolumeServiceError(
            "Dataset is missing required columns for order volume analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )
    frame[ORDER_ID_COLUMN] = frame[ORDER_ID_COLUMN].astype(str).str.strip()

    frame = frame.dropna(subset=[DATE_COLUMN])
    frame = frame[frame[ORDER_ID_COLUMN] != ""]

    return frame


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_order_volume_by_day(dataset_file_path, year, month):
    year = int(year)
    month = int(month)

    frame = _read_dataset_frame(dataset_file_path)
    filtered = frame[
        (frame[DATE_COLUMN].dt.year == year)
        & (frame[DATE_COLUMN].dt.month == month)
    ]

    days_in_month = calendar.monthrange(year, month)[1]

    if filtered.empty:
        return {
            "days_in_month": days_in_month,
            "total_orders": 0,
            "points": [
                {
                    "day": day,
                    "count": 0,
                }
                for day in range(1, days_in_month + 1)
            ],
        }

    grouped = (
        filtered.groupby(filtered[DATE_COLUMN].dt.day)[ORDER_ID_COLUMN]
        .nunique()
        .reindex(range(1, days_in_month + 1), fill_value=0)
    )

    points = [
        {
            "day": int(day),
            "count": int(grouped.loc[day]),
        }
        for day in range(1, days_in_month + 1)
    ]

    total_orders = int(sum(point["count"] for point in points))

    return {
        "days_in_month": days_in_month,
        "total_orders": total_orders,
        "points": points,
    }
