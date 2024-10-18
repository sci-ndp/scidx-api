import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

def apply_window_filter(df, window_size, statistic, condition):
    """
    Applies a rolling window filter on the DataFrame and evaluates the condition.
    """
    # Parse the condition (e.g., "fixed acidity > 7.5")
    field, operator, value = parse_condition(condition)
    
    # Ensure the field exists in the DataFrame
    if field not in df.columns:
        logger.error(f"Field '{field}' not found in DataFrame.")
        return pd.Series([False] * len(df), index=df.index)
    
    # Apply rolling window operation
    if statistic == "mean":
        windowed_series = df[field].rolling(window=window_size).mean()
    elif statistic == "sum":
        windowed_series = df[field].rolling(window=window_size).sum()
    elif statistic == "min":
        windowed_series = df[field].rolling(window=window_size).min()
    elif statistic == "max":
        windowed_series = df[field].rolling(window=window_size).max()
    elif statistic == "std":
        windowed_series = df[field].rolling(window=window_size).std()
    else:
        logger.error(f"Unsupported statistic '{statistic}' for window filtering.")
        return pd.Series([False] * len(df), index=df.index)

    # Evaluate the condition against the windowed series
    return eval_condition_on_series(windowed_series, operator, value)

def eval_condition_on_series(series, operator, value):
    """Evaluates the condition for a given series and operator."""
    value = float(value)  # Convert value to float for comparison
    comparison_map = {
        '>=': series >= value,
        '>': series > value,
        '<=': series <= value,
        '<': series < value,
        '!=': series != value,
        '=': series == value,
    }
    return comparison_map.get(operator, pd.Series([False] * len(series), index=series.index))

def parse_condition(condition):
    """Parse a condition string into field, operator, and value."""
    operators = ['>=', '>', '<=', '<', '!=', '=']
    for op in operators:
        if f" {op} " in condition:
            field, value = re.split(rf'\s{op}\s', condition, maxsplit=1)
            return field.strip(), op, value.strip()
    raise ValueError(f"Invalid condition: {condition}")
