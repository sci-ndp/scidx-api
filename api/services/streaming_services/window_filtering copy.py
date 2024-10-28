import pandas as pd
import logging
import re

logger = logging.getLogger(__name__)

def apply_window_filter(df, window_size, statistic, condition):
    """
    Applies a rolling window filter on the DataFrame and evaluates the condition.
    Rows with insufficient data points for the window size will be marked as False.
    """
    field, operator, value = parse_condition(condition)
    
    if field not in df.columns:
        logger.error(f"Field '{field}' not found in DataFrame.")
        return pd.Series([False] * len(df), index=df.index)

    if statistic == "mean":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).mean()
    elif statistic == "sum":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).sum()
    elif statistic == "min":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).min()
    elif statistic == "max":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).max()
    elif statistic == "std":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).std()
    else:
        logger.error(f"Unsupported statistic '{statistic}' for window filtering.")
        return pd.Series([False] * len(df), index=df.index)

    return eval_condition_on_series(windowed_series, operator, value)


def apply_window_filter_if_else_with_nan(df, window_size, statistic, condition, action_field):
    """
    Applies a rolling window filter specifically for IF-THEN-ELSE statements and returns
    a mask to track where NaN values are due to insufficient window size.
    """
    field, operator, value = parse_condition(condition)

    if field not in df.columns:
        logger.error(f"Field '{field}' not found in DataFrame.")
        return pd.Series([None] * len(df), pd.Series([False] * len(df)))

    if statistic == "mean":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).mean()
    elif statistic == "sum":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).sum()
    elif statistic == "min":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).min()
    elif statistic == "max":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).max()
    elif statistic == "std":
        windowed_series = df[field].rolling(window=window_size, min_periods=window_size).std()
    else:
        logger.error(f"Unsupported statistic '{statistic}' for window filtering.")
        return pd.Series([None] * len(df), pd.Series([False] * len(df)))

    # Evaluate the condition with the windowed series, ensuring NaN handling
    result = eval_condition_on_series_with_nan(windowed_series, operator, value)

    # Boolean mask to track NaN due to insufficient window data
    is_window_nan = windowed_series.isna()

    # If the column already exists, only update the values that are not NaN
    if action_field in df.columns:
        result.loc[windowed_series.isna()] = df[action_field].loc[windowed_series.isna()]
    else:
        result.loc[windowed_series.isna()] = None  # Return None for insufficient data

    return result, is_window_nan


def eval_condition_on_series_with_nan(series, operator, value):
    """Evaluates the condition for a given series and operator.
    For values that are NaN (due to insufficient window data), returns None.
    """
    # Create a series of None values initially
    result = pd.Series([None] * len(series), index=series.index)
    
    # Convert value to float for comparison
    value = float(value)
    
    # Comparison map
    comparison_map = {
        '>=': series >= value,
        '>': series > value,
        '<=': series <= value,
        '<': series < value,
        '!=': series != value,
        '=': series == value,
    }

    # Apply the condition for non-NaN values (i.e., only after enough data for the window)
    condition_result = comparison_map.get(operator)
    
    # Only apply the result for rows where the window has enough data (i.e., not NaN)
    result.loc[series.notna()] = condition_result.loc[series.notna()]
    
    return result

def eval_condition_on_series(series, operator, value):
    """Evaluates the condition for a given series and operator."""
    value = float(value)
    comparison_map = {
        '>=': series >= value,
        '>': series > value,
        '<=': series < value,
        '<': series < value,
        '!=': series != value,
        '=': series == value,
    }
    return comparison_map.get(operator)

def parse_condition(condition):
    """Parse a condition string into field, operator, and value."""
    operators = ['>=', '>', '<=', '<', '!=', '=']
    for op in operators:
        if f" {op} " in condition:
            field, value = re.split(rf'\s{op}\s', condition, maxsplit=1)
            return field.strip(), op, value.strip()
    raise ValueError(f"Invalid condition: {condition}")
