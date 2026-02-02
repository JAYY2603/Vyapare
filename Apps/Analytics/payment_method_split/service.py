from pathlib import Path

import pandas as pd


DATE_COLUMN = "Date"
PAYMENT_TYPE_COLUMN = "PaymentType"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class PaymentMethodSplitServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, PAYMENT_TYPE_COLUMN],
        )
    except Exception as exc:
        raise PaymentMethodSplitServiceError(
            "Unable to read dataset file.") from exc

    if DATE_COLUMN not in frame.columns or PAYMENT_TYPE_COLUMN not in frame.columns:
        raise PaymentMethodSplitServiceError(
            "Dataset is missing required columns for payment method analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )

    frame[PAYMENT_TYPE_COLUMN] = (
        frame[PAYMENT_TYPE_COLUMN]
        .astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
    )

    return frame.dropna(subset=[DATE_COLUMN])


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_payment_method_split(dataset_file_path, year, month=None):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]
    if month is not None:
        filtered = filtered[filtered[DATE_COLUMN].dt.month == int(month)]

    if filtered.empty:
        return {
            "total_records": 0,
            "split": [],
        }

    grouped = (
        filtered.groupby(PAYMENT_TYPE_COLUMN)
        .size()
        .reset_index(name="count")
        .sort_values(by="count", ascending=False)
    )

    total_records = int(grouped["count"].sum())
    split_payload = []

    for _, row in grouped.iterrows():
        count = int(row["count"])
        split_payload.append(
            {
                "payment_method": str(row[PAYMENT_TYPE_COLUMN]),
                "count": count,
                "percentage": round((count / total_records) * 100, 2),
            }
        )

    return {
        "total_records": total_records,
        "split": split_payload,
    }
