import pandas as pd


DATE_COLUMN = "Date"
CATEGORY_COLUMN = "Category"
PAYMENT_TYPE_COLUMN = "PaymentType"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class PaymentVsCategoryServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, CATEGORY_COLUMN, PAYMENT_TYPE_COLUMN],
        )
    except Exception as exc:
        raise PaymentVsCategoryServiceError(
            "Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, CATEGORY_COLUMN, PAYMENT_TYPE_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise PaymentVsCategoryServiceError(
            "Dataset is missing required columns for payment vs category analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )

    frame[CATEGORY_COLUMN] = (
        frame[CATEGORY_COLUMN]
        .astype(str)
        .str.strip()
        .replace({"": "Unknown", "nan": "Unknown", "None": "Unknown"})
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


def get_payment_vs_category(dataset_file_path, year, month=None):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]
    if month is not None:
        filtered = filtered[filtered[DATE_COLUMN].dt.month == int(month)]

    if filtered.empty:
        return {
            "total_records": 0,
            "payment_methods": [],
            "categories": [],
        }

    grouped = (
        filtered.groupby([CATEGORY_COLUMN, PAYMENT_TYPE_COLUMN])
        .size()
        .reset_index(name="count")
    )

    category_totals = (
        grouped.groupby(CATEGORY_COLUMN)["count"]
        .sum()
        .sort_values(ascending=False)
    )
    payment_totals = (
        grouped.groupby(PAYMENT_TYPE_COLUMN)["count"]
        .sum()
        .sort_values(ascending=False)
    )

    ordered_categories = category_totals.index.tolist()
    ordered_payment_methods = payment_totals.index.tolist()

    category_rows = []
    for category in ordered_categories:
        category_slice = grouped[grouped[CATEGORY_COLUMN] == category]
        category_total = int(category_slice["count"].sum())

        split_payload = []
        for payment_method in ordered_payment_methods:
            match = category_slice[
                category_slice[PAYMENT_TYPE_COLUMN] == payment_method
            ]
            count = int(match["count"].iloc[0]) if not match.empty else 0
            percentage = round((count / category_total) *
                               100, 2) if category_total else 0.0

            split_payload.append(
                {
                    "payment_method": str(payment_method),
                    "count": count,
                    "percentage": percentage,
                }
            )

        category_rows.append(
            {
                "category": str(category),
                "total_records": category_total,
                "split": split_payload,
            }
        )

    return {
        "total_records": int(grouped["count"].sum()),
        "payment_methods": [str(method) for method in ordered_payment_methods],
        "categories": category_rows,
    }
