import json
import re
from pathlib import Path
from urllib import error as url_error
from urllib import request as url_request

import pandas as pd
from django.conf import settings
from rest_framework import status


BUSINESS_SYSTEM_PROMPT = (
    "You are Vyapare Business Assistant, an AI assistant for a retail/business management platform. "
    "You must only answer questions related to business operations, sales boosting, profit maximization, "
    "inventory, pricing, promotions, customer retention, forecasting, cost control, and data-driven decisions. "
    "If a question is outside these topics, politely refuse and redirect the user to ask business-related questions. "
    "Keep responses concise, practical, and action-oriented."
)

DATASET_SYSTEM_PROMPT = (
    "You are Vyapare Dataset Assistant. Answer user questions using only the provided dataset context. "
    "If the answer cannot be derived from the dataset context, clearly say that and suggest what columns or data are needed. "
    "Prefer concise, practical answers and include numeric evidence when available."
)

MAX_DATASET_CONTEXT_CHARS = 7000

BUSINESS_KEYWORDS = {
    "business",
    "sale",
    "sales",
    "profit",
    "profits",
    "revenue",
    "inventory",
    "inventories",
    "pricing",
    "price",
    "prices",
    "margin",
    "margins",
    "customer",
    "customers",
    "marketing",
    "promotion",
    "promotions",
    "forecast",
    "forecasting",
    "demand",
    "order",
    "orders",
    "stock",
    "stocks",
    "cost",
    "costs",
    "retail",
    "upsell",
    "cross-sell",
    "cross sell",
    "growth",
    "strategy",
    "strategies",
    "operation",
    "operations",
    "trend",
    "trending",
    "month",
    "year",
    "cashflow",
    "cash flow",
    "conversion",
    "store",
}


class ChatbotServiceError(Exception):
    def __init__(self, message, status_code=status.HTTP_502_BAD_GATEWAY, detail=""):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail


def _contains_business_keyword(text):
    normalized = (text or "").strip().lower()
    if not normalized:
        return False

    compact = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    compact = re.sub(r"\s+", " ", compact).strip()

    for keyword in BUSINESS_KEYWORDS:
        if keyword in compact:
            return True

    return False


def _is_short_follow_up(text):
    normalized = (text or "").strip().lower()
    if not normalized:
        return False

    # Allow short replies such as "1", "yes", "go ahead" when context is business.
    if normalized.isdigit():
        return True

    if len(normalized) <= 20:
        return normalized in {
            "yes",
            "no",
            "ok",
            "okay",
            "sure",
            "continue",
            "go ahead",
            "next",
            "first",
            "second",
            "third",
        }

    return False


def _history_has_business_context(history):
    if not isinstance(history, list):
        return False

    for item in history[-6:]:
        if not isinstance(item, dict):
            continue
        content = str(item.get("content", "")).strip()
        if _contains_business_keyword(content):
            return True

    return False


def is_business_query(user_message, history=None):
    normalized = (user_message or "").strip().lower()
    if not normalized:
        return False

    if _contains_business_keyword(normalized):
        return True

    if _is_short_follow_up(normalized) and _history_has_business_context(history):
        return True

    return False


def _sanitize_history(history):
    safe_history = []
    if isinstance(history, list):
        for item in history[-8:]:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "")).strip().lower()
            content = str(item.get("content", "")).strip()
            if role in {"user", "assistant"} and content:
                safe_history.append({"role": role, "content": content})
    return safe_history


def build_dataset_context(uploaded_file):
    extension = Path((uploaded_file.name or "")).suffix.lower()

    try:
        if extension in {".xlsx", ".xls"}:
            frame = pd.read_excel(uploaded_file)
        elif extension == ".csv":
            frame = pd.read_csv(uploaded_file)
        else:
            raise ValueError("Unsupported file format.")
    except Exception as exc:
        raise ValueError(
            "Unable to read dataset. Please upload a valid Excel or CSV file.") from exc

    frame = frame.dropna(axis=0, how="all")
    if frame.empty:
        raise ValueError("The uploaded dataset is empty.")

    frame.columns = [str(col).strip() for col in frame.columns]
    row_count = int(frame.shape[0])
    column_count = int(frame.shape[1])
    columns = frame.columns.tolist()

    dtype_parts = [f"{col}: {str(dtype)}" for col,
                   dtype in frame.dtypes.items()]

    preview_rows = frame.head(20).copy()
    preview_rows = preview_rows.where(pd.notna(preview_rows), None)
    for col in preview_rows.columns:
        preview_rows[col] = preview_rows[col].apply(
            lambda val: None if val is None else str(val)[:80]
        )

    preview_records = preview_rows.to_dict(orient="records")

    dataset_context = (
        f"Dataset name: {uploaded_file.name}\n"
        f"Rows: {row_count}\n"
        f"Columns ({column_count}): {', '.join(columns)}\n"
        f"Column types: {'; '.join(dtype_parts)}\n"
        f"Sample rows (first {len(preview_records)}): {json.dumps(preview_records, ensure_ascii=True)}"
    )

    dataset_context = dataset_context[:MAX_DATASET_CONTEXT_CHARS]

    metadata = {
        "name": uploaded_file.name,
        "rows": row_count,
        "columns": column_count,
        "column_names": columns,
    }

    return dataset_context, metadata


def _build_payload(user_message, history, dataset_context=""):
    messages = []
    if dataset_context:
        messages.append({"role": "system", "content": DATASET_SYSTEM_PROMPT})
        messages.append(
            {"role": "system", "content": f"DATASET_CONTEXT:\n{dataset_context}"})
    else:
        messages.append({"role": "system", "content": BUSINESS_SYSTEM_PROMPT})

    return {
        "model": settings.GROQ_MODEL,
        "temperature": 0.2,
        "max_tokens": 500,
        "messages": [*messages, *_sanitize_history(history), {"role": "user", "content": user_message}],
    }


def generate_business_reply(user_message, history, dataset_context=""):
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ChatbotServiceError(
            "Chatbot is not configured. Please set GROQ_API_KEY in environment variables.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    req = url_request.Request(
        url="https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(_build_payload(user_message, history,
                        dataset_context=dataset_context)).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Vyapare/1.0 (+Django urllib)",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with url_request.urlopen(req, timeout=25) as resp:
            response_payload = json.loads(resp.read().decode("utf-8"))
    except url_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
        raise ChatbotServiceError(
            f"Groq API error ({exc.code}).",
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=raw[:500],
        )
    except Exception as exc:
        raise ChatbotServiceError(
            "Unable to reach chatbot provider right now.",
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    choices = response_payload.get("choices") or []
    if not choices:
        raise ChatbotServiceError(
            "Chatbot returned an empty response.",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )

    reply = choices[0].get("message", {}).get("content", "").strip()
    if not reply:
        return "I could not generate a response right now."

    return reply
