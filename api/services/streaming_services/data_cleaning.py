import pandas as pd
import logging
import re

from .window_filtering import apply_window_filter, apply_window_filter_if_else_with_nan

logger = logging.getLogger(__name__)

def mapped_values_vectorized(mapping, df):
    result = pd.DataFrame(index=df.index)

    if mapping is None:
        result = df.copy()  # If no mapping is provided, include all columns
    else:
        for key, path in mapping.items():
            if '[' in path and ']' in path:
                # Extract the field name and index
                field, index = re.match(r"(.*)\[(\d+)\]", path).groups()
                index = int(index)

                if field in df.columns:
                    result[key] = df[field].apply(lambda x: x[index] if isinstance(x, list) and len(x) > index else None)
            elif path in df.columns:
                if 'timestamp' in key.lower():
                    result[key] = pd.to_datetime(df[path], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    result[key] = df[path]
            else:
                logger.warning(f"Mapping key '{key}' does not exist in dataframe.")
    return result

def eval_condition(condition, df):
    condition = condition.strip()

    # Handling parentheses first (recursive evaluation of conditions inside parentheses)
    while '(' in condition and ')' in condition:
        inner_condition = re.search(r'\(([^()]+)\)', condition).group(1)
        inner_result = eval_condition(inner_condition, df)
        condition = condition.replace(f"({inner_condition})", str(inner_result))

    # Splitting on OR first
    if ' OR ' in condition:
        sub_conditions = condition.split(' OR ')
        return pd.concat([eval_condition(sub.strip(), df) for sub in sub_conditions], axis=1).any(axis=1)

    # Splitting on AND second
    if ' AND ' in condition:
        sub_conditions = condition.split(' AND ')
        return pd.concat([eval_condition(sub.strip(), df) for sub in sub_conditions], axis=1).all(axis=1)

    # Parsing the field, operator, and value
    field, operator, value = parse_condition(condition)

    # Check if the field exists in the dataframe
    if field not in df.columns:
        logger.error(f"Column '{field}' does not exist in the dataframe.")
        return pd.Series([False] * len(df), index=df.index)

    # Log the values before applying the condition
    logger.info(f"Evaluating condition: {condition}")
    logger.info(f"Column '{field}' before processing: {df[field].head()}")

    # Cast the column values to strings for the IN operator
    if operator == 'IN':
        df[field] = df[field].astype(str)
        logger.info(f"Column '{field}' after casting to string: {df[field].head()}")

    # Handle the IN condition separately
    if operator == 'IN':
        try:
            if isinstance(value, str):
                value_list = eval(value)
            else:
                value_list = value

            if not isinstance(value_list, list):
                logger.error(f"Invalid list for IN condition: '{value}' in condition '{condition}'")
                return pd.Series([False] * len(df), index=df.index)

            return df[field].isin(value_list)
        except Exception as e:
            logger.error(f"Error parsing list for IN condition: '{value}' in condition '{condition}': {e}")
            return pd.Series([False] * len(df), index=df.index)

    # Apply comparison operators (e.g., >=, >, etc.)
    try:
        value_values = pd.to_numeric(value, errors='raise')
    except ValueError:
        value_values = value.strip("'\"")
        df[field] = df[field].astype(str)

    comparison_map = {
        '>=': df[field] >= value_values,
        '>': df[field] > value_values,
        '<=': df[field] <= value_values,
        '<': df[field] < value_values,
        '!=': df[field] != value_values,
        '=': df[field] == value_values,
    }

    result = comparison_map.get(operator)
    if result is not None:
        return result

    logger.error(f"Unknown operator '{operator}' in condition '{condition}'")
    return pd.Series([False] * len(df), index=df.index)




def parse_condition(condition):
    operators = ['>=', '>', '<=', '<', '!=', '=', 'IN']
    for op in operators:
        if f" {op} " in condition:
            field, value = re.split(rf'\s{op}\s', condition, maxsplit=1)
            field = field.strip('\'"')
            return field.strip(), op, value.strip()
    raise ValueError(f"Invalid condition: {condition}")

def evaluate_expression(expression, df):
    expression = expression.strip()

    # Check if the expression is a list
    if expression.startswith('[') and expression.endswith(']'):
        try:
            return eval(expression)
        except Exception as e:
            logger.error(f"Error evaluating list expression '{expression}': {e}")
            return pd.Series([None] * len(df), index=df.index)

    # Treat the expression as a string literal if it doesn't contain any operators or column names
    if not any(op in expression for op in ['+', '-', '*', '/']) and expression not in df.columns:
        try:
            return float(expression)
        except ValueError:
            return expression.strip("'").strip('"')  # Handle it as a string

    # Replace column names with their corresponding series
    for column in df.columns:
        if column in expression:
            expression = expression.replace(column, f"df['{column}']")

    try:
        return eval(expression)
    except Exception as e:
        logger.error(f"Error evaluating expression '{expression}': {e}")
        return pd.Series([None] * len(df), index=df.index)


def apply_if_then_rules(df, rules):
    if not rules:
        return df

    for rule in rules:
        try:
            if "IF" in rule and "THEN" in rule:
                if_part, then_else_part = rule.split("THEN", 1)
                if_conditions = if_part.replace("IF", "").strip()

                then_part, else_part = None, None
                if "ELSE" in then_else_part:
                    then_part, else_part = then_else_part.split("ELSE", 1)
                else:
                    then_part = then_else_part
                
                # Check if the IF condition contains a window_filter
                if "window_filter" in if_conditions:
                    match = re.match(r"window_filter\((\d+),\s*(\w+),\s*(.+)\)", if_conditions)
                    if match:
                        window_size = int(match.group(1))
                        statistic = match.group(2)
                        condition_str = match.group(3)

                        # Apply window filter specifically for IF-THEN-ELSE
                        action_field, action_value = parse_then_action(then_part.strip())
                        matches, is_window_nan = apply_window_filter_if_else_with_nan(df, window_size, statistic, condition_str, action_field)
                    else:
                        logger.error(f"Invalid window_filter format in IF condition: {if_conditions}")
                        continue
                else:
                    # Evaluate regular IF condition
                    matches = eval_condition(if_conditions, df)
                    is_window_nan = pd.Series([False] * len(df))  # No window-based NaNs for regular conditions

                # Apply THEN action
                if matches is not None and matches.any():
                    action_field, action_value = parse_then_action(then_part.strip())
                    if action_field not in df.columns:
                        df[action_field] = None  # Create column if not exists

                    # Only update where matches are True, and window is fully populated (non-NaN)
                    df.loc[matches == True, action_field] = evaluate_expression(action_value, df)

                # Apply ELSE action if present
                if else_part:
                    non_matches = ~matches.fillna(False)
                    action_field, action_value = parse_then_action(else_part.strip())

                    # If column exists, don't rely on NaN checks
                    if action_field in df.columns:
                        # Apply ELSE directly to all non-matching rows (skip NaN checks for existing columns)
                        df.loc[non_matches == True, action_field] = evaluate_expression(action_value, df)
                    else:
                        # Apply ELSE only where the column remains NaN after THEN and is not due to window insufficiency
                        df[action_field] = None  # Create column if not exists
                        df.loc[(df[action_field].isna()) & (non_matches == True) & (~is_window_nan), action_field] = evaluate_expression(action_value, df)

        except Exception as e:
            logger.error(f"Error applying rule '{rule}': {e}")

    return df




def parse_then_action(action):
    if "=" in action:
        field, value = action.split("=", 1)
        return field.strip(), value.strip()
    raise ValueError(f"Invalid action: {action}")


def safely_convert_to_numeric(df, column):
    """
    Tries to convert a column to numeric values.
    If the conversion results in all NaN, reverts to string type.
    """
    original_column = df[column].copy()
    
    # Try converting to numeric
    df[column] = pd.to_numeric(df[column], errors='coerce')
    
    # Check if the conversion led to all NaN values
    if df[column].isna().all():
        # If all values are NaN after conversion, revert to original string values
        df[column] = original_column.astype(str)
        logger.info(f"Column '{column}' was reverted to string type after failed numeric conversion.")
    else:
        logger.info(f"Column '{column}' successfully converted to numeric.")

    return df[column]


def apply_filters_and_rules(df, filter_semantics):
    """
    Apply filters and rules in chronological order.
    Detect window_filter and apply it before continuing with the rest.
    """
    if not filter_semantics:
        return df

    filtered_df = df.copy()

    # Apply each filter or rule in the order they appear
    for idx, condition in enumerate(filter_semantics):
        try:
            # Check if this is a window_filter condition
            if condition.startswith("window_filter"):
                # Extract window parameters: window_filter(window_size, statistic, condition)
                match = re.match(r"window_filter\((\d+),\s*(\w+),\s*(.+)\)", condition)
                if match:
                    window_size = int(match.group(1))
                    statistic = match.group(2)
                    condition_str = match.group(3)
                    
                    # Apply the window filter and reduce the DataFrame based on results
                    matches = apply_window_filter(filtered_df, window_size, statistic, condition_str)
                    filtered_df = filtered_df[matches]  # Keep only rows that match
                else:
                    logger.error(f"Invalid window_filter format: {condition}")
                    continue

            # Regular conditions (non-window filters)
            elif "IF" in condition and "THEN" in condition:
                # Apply IF-THEN rules
                filtered_df = apply_if_then_rules(filtered_df, [condition])
            else:
                # Apply other regular conditions
                matches = eval_condition(condition, filtered_df)
                filtered_df = filtered_df[matches]

            # After each condition, ensure all columns are properly typed
            for column in filtered_df.columns:
                if filtered_df[column].dtype == 'object':  # Check object (string) columns
                    filtered_df[column] = safely_convert_to_numeric(filtered_df, column)
                
        except Exception as e:
            logger.error(f"Error applying condition '{condition}': {e}")

    return filtered_df



async def process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, if_then_rules=None, additional_info=None):
    async with buffer_lock:
        df = pd.DataFrame(messages)
        
        mapped_data = mapped_values_vectorized(mapping, df)
        logger.info(f"Mapped data: {mapped_data.head(5)}")

        # Apply all filters and rules in chronological order
        filtered_data = apply_filters_and_rules(mapped_data, filter_semantics)
        logger.info(f"Filtered data: {filtered_data.head(5)}")

        # Use the final filtered data
        if not filtered_data.empty:
            if additional_info:
                if isinstance(additional_info, dict):
                    stream.extras.update(additional_info)
                elif isinstance(additional_info, str):
                    stream.extras['additional_info'] = additional_info
                else:
                    stream.extras['additional_info'] = str(additional_info)
            await send_data(filtered_data, stream, loop)
        else:
            logger.warning("No data after filtering.")
