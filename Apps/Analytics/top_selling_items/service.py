import pandas as pd


DATE_COLUMN = "Date"
ITEM_COLUMN = "Item"
QUANTITY_COLUMN = "Quantity"
DATE_FORMAT = "%d/%m/%Y/%H:%M:%S"
MAX_ITEMS = 20


class TopSellingItemsServiceError(Exception):
    pass


def _read_dataset_frame(dataset_file_path):
    try:
        frame = pd.read_excel(
            dataset_file_path,
            usecols=[DATE_COLUMN, ITEM_COLUMN, QUANTITY_COLUMN],
        )
    except Exception as exc:
        raise TopSellingItemsServiceError(
            "Unable to read dataset file.") from exc

    required_columns = {DATE_COLUMN, ITEM_COLUMN, QUANTITY_COLUMN}
    if not required_columns.issubset(set(frame.columns)):
        raise TopSellingItemsServiceError(
            "Dataset is missing required columns for top selling items analytics."
        )

    frame[DATE_COLUMN] = pd.to_datetime(
        frame[DATE_COLUMN],
        format=DATE_FORMAT,
        errors="coerce",
    )
    frame[ITEM_COLUMN] = frame[ITEM_COLUMN].astype(str).str.strip()
    frame[QUANTITY_COLUMN] = pd.to_numeric(
        frame[QUANTITY_COLUMN], errors="coerce").fillna(0)

    frame = frame.dropna(subset=[DATE_COLUMN])
    frame = frame[frame[ITEM_COLUMN] != ""]

    return frame


def get_available_years(dataset_file_path):
    frame = _read_dataset_frame(dataset_file_path)
    years = sorted(frame[DATE_COLUMN].dt.year.unique().tolist())
    return [int(year) for year in years]


def get_top_selling_items(dataset_file_path, year, month=None):
    frame = _read_dataset_frame(dataset_file_path)

    filtered = frame[frame[DATE_COLUMN].dt.year == int(year)]
    if month is not None:
        filtered = filtered[filtered[DATE_COLUMN].dt.month == int(month)]

    if filtered.empty:
        return {
            "total_quantity": 0,
            "points": [],
        }

    grouped = (
        filtered.groupby(ITEM_COLUMN)[QUANTITY_COLUMN]
        .sum()
        .reset_index(name="quantity")
        .sort_values(by="quantity", ascending=False)
        .head(MAX_ITEMS)
    )

    points = []
    for _, row in grouped.iterrows():
        points.append(
            {
                "label": str(row[ITEM_COLUMN]),
                "quantity": int(round(float(row["quantity"]))),
            }
        )

    total_quantity = int(sum(point["quantity"] for point in points))

    return {
        "total_quantity": total_quantity,
        "points": points,
    }
