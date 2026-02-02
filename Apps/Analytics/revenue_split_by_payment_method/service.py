import pandas as pd


DATE_COLUMN = "Date"
PAYMENT_TYPE_COLUMN = "PaymentType"
PRICE_COLUMN = "Price"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"


class RevenueSplitByPaymentMethodServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, PAYMENT_TYPE_COLUMN, PRICE_COLUMN],
        )
    except Exception as exc:
        raise RevenueSplitByPaymentMethodServiceError(
            "Unable to read dataset file."
        ) from exc

    required_columns = {DATE_COLUMN, PAYMENT_TYPE_COLUMN, PRICE_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise RevenueSplitByPaymentMethodServiceError(
            "Dataset is missing required columns for revenue split analytics."
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

    frame[PRICE_COLUMN] = pd.to_numeric(
        frame[PRICE_COLUMN], errors="coerce").fillna(0)
    frame = frame.dropna(subset=[DATE_COLUMN])

    return frame


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_revenue_split(dataset_file_path, year, month=None):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]
    if month is not None:
        filtered = filtered[filtered[DATE_COLUMN].dt.month == int(month)]

    if filtered.empty:
        return {
            "total_revenue": 0.0,
            "split": [],
        }

    grouped = (
        filtered.groupby(PAYMENT_TYPE_COLUMN)[PRICE_COLUMN]
        .sum()
        .reset_index(name="revenue")
        .sort_values(by="revenue", ascending=False)
    )

    total_revenue = float(grouped["revenue"].sum())
    if total_revenue <= 0:
        return {
            "total_revenue": 0.0,
            "split": [],
        }

    split_payload = []
    for _, row in grouped.iterrows():
        revenue = float(row["revenue"])
        split_payload.append(
            {
                "payment_method": str(row[PAYMENT_TYPE_COLUMN]),
                "revenue": round(revenue, 2),
                "percentage": round((revenue / total_revenue) * 100, 2),
            }
        )

    return {
        "total_revenue": round(total_revenue, 2),
        "split": split_payload,
    }
