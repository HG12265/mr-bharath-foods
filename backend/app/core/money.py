from decimal import Decimal
from typing import Any

from bson.decimal128 import Decimal128


def convert_decimals_to_bson(data: Any) -> Any:
    """
    Recursively scans and converts Python Decimal values to BSON Decimal128 objects
    to ensure database compatibility.
    """
    if isinstance(data, dict):
        return {k: convert_decimals_to_bson(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimals_to_bson(v) for v in data]
    elif isinstance(data, Decimal):
        return Decimal128(data)
    return data


def convert_bson_to_decimals(data: Any) -> Any:
    """
    Recursively scans and converts BSON Decimal128 objects to Python Decimal values
    to ensure precision-safe business operations.
    """
    if isinstance(data, dict):
        return {k: convert_bson_to_decimals(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_bson_to_decimals(v) for v in data]
    elif isinstance(data, Decimal128):
        return data.to_decimal()
    return data
