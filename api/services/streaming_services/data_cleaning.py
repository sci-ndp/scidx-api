import pandas as pd
import logging
import re

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

    field, operator, value = parse_condition(condition)

    if '[' in field and ']' in field:
        field_name, field_index = re.match(r"(.*)\[(\d+)\]", field).groups()
        field_index = int(field_index)
        field_values = df[field_name].apply(lambda x: x[field_index] if isinstance(x, list) and len(x) > field_index else None)
    else:
        field_values = evaluate_expression(field, df)

    if operator == 'IN':
        try:
            value_list = eval(value) if isinstance(value, str) else value
            if not isinstance(value_list, list):
                logger.error(f"Invalid list for IN condition: '{value}' in condition '{condition}'")
                return pd.Series([False] * len(df), index=df.index)
        except Exception as e:
            logger.error(f"Error parsing list for IN condition: '{value}' in condition '{condition}': {e}")
            return pd.Series([False] * len(df), index=df.index)
        return field_values.isin(value_list)
    
    else:
        value_values = evaluate_expression(value, df)

    # Apply the comparison
    if operator == '>=':
        return field_values >= value_values
    elif operator == '>':
        return field_values > value_values
    elif operator == '<=':
        return field_values <= value_values
    elif operator == '<':
        return field_values < value_values
    elif operator == '!=':
        return field_values != value_values
    elif operator == '=':
        return field_values == value_values

    return pd.Series([False] * len(df), index=df.index)


def parse_condition(condition):
    # Adjust to capture the 'IN' condition correctly
    operators = ['>=', '>', '<=', '<', '!=', '=', 'IN']
    for op in operators:
        # Use regex to correctly identify the IN condition especially with lists
        if f" {op} " in condition:
            field, value = re.split(rf'\s{op}\s', condition, maxsplit=1)
            return field.strip(), op, value.strip()
    raise ValueError(f"Invalid condition: {condition}")

def evaluate_expression(expression, df):
    """
    Evaluate mathematical expressions, literal strings, or lists in the context of the dataframe.
    """
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
        if expression.isdigit():
            return float(expression)
        return expression.strip().strip("'").strip('"')  # Handle it as a string

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
                
                # Evaluate the IF condition
                matches = eval_condition(if_conditions, df)

                # Apply THEN action
                if matches.any():
                    action_field, action_value = parse_then_action(then_part.strip())
                    if action_field not in df.columns:
                        df[action_field] = None

                    # Apply mathematical expression
                    df.loc[matches, action_field] = evaluate_expression(action_value, df.loc[matches])

                # Apply ELSE action
                if else_part:
                    non_matches = ~matches
                    action_field, action_value = parse_then_action(else_part.strip())

                    if action_field not in df.columns:
                        df[action_field] = None

                    # Apply mathematical expression
                    df.loc[non_matches, action_field] = evaluate_expression(action_value, df.loc[non_matches])

        except Exception as e:
            logger.error(f"Error applying rule '{rule}': {e}")

    return df


def apply_filters_vectorized(df, filter_semantics):
    if not filter_semantics:
        return df

    filtered_df = df.copy()
    for filter_condition in filter_semantics:
        try:
            matches = eval_condition(filter_condition, filtered_df)
            filtered_df = filtered_df[matches]
                
        except Exception as e:
            logger.error(f"Error applying filter '{filter_condition}': {e}")

    return filtered_df


def parse_then_action(action):
    if "=" in action:
        field, value = action.split("=", 1)
        return field.strip(), value.strip()
    raise ValueError(f"Invalid action: {action}")


async def process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, if_then_rules=None, additional_info=None):
    async with buffer_lock:
        df = pd.DataFrame(messages)
        mapped_data = mapped_values_vectorized(mapping, df)

        # Separate IF-THEN rules from regular filters
        extracted_if_then_rules = [rule for rule in filter_semantics if "IF" in rule and "THEN" in rule]
        remaining_filters = [f for f in filter_semantics if f not in extracted_if_then_rules]

        # Apply the regular filters first, step by step
        filtered_data = apply_filters_vectorized(mapped_data, remaining_filters)

        # Apply IF-THEN rules to the filtered data
        if extracted_if_then_rules:
            filtered_data = apply_if_then_rules(filtered_data, extracted_if_then_rules)

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
            pass  # No data after filtering