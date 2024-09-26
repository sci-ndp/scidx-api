import pandas as pd
import logging

logger = logging.getLogger(__name__)

def mapped_values_vectorized(mapping, df):
    result = pd.DataFrame(index=df.index)
    
    if mapping is None:
        result = df.copy()  # If no mapping is provided, include all columns
    else:
        for key, path in mapping.items():
            if path in df.columns:
                if 'timestamp' in key.lower():
                    result[key] = pd.to_datetime(df[path], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    result[key] = df[path]
    return result

def apply_if_then_rules(df, rules):
    if not rules:
        return df

    for rule in rules:
        try:
            if "IF" in rule and "THEN" in rule:
                if_part, then_part = rule.split("THEN", 1)
                if_conditions = if_part.replace("IF", "").strip().split("AND")

                matches = pd.Series([True] * len(df), index=df.index)
                for condition in if_conditions:
                    condition = condition.strip()
                    field, operator, value = parse_condition(condition)

                    if field not in df.columns:
                        matches &= False
                        continue

                    if operator == ">=":
                        matches &= df[field].astype(float) >= float(value)
                    elif operator == ">":
                        matches &= df[field].astype(float) > float(value)
                    elif operator == "<=":
                        matches &= df[field].astype(float) <= float(value)
                    elif operator == "<":
                        matches &= df[field].astype(float) < float(value)
                    elif operator == "!=":
                        matches &= df[field] != value
                    elif operator == "=":
                        matches &= df[field] == value

                if matches.any():
                    action_field, action_value = parse_then_action(then_part.strip())

                    # Ensure the action_field exists, if not create it with default value None
                    if action_field not in df.columns:
                        df[action_field] = None

                    # Convert action_value to match the data type
                    try:
                        if pd.api.types.is_numeric_dtype(df[action_field]):
                            action_value = pd.to_numeric(action_value, errors='coerce')
                        elif pd.api.types.is_datetime64_any_dtype(df[action_field]):
                            action_value = pd.to_datetime(action_value, errors='coerce')
                        else:
                            action_value = str(action_value)
                    except Exception as e:
                        logger.error(f"Failed to convert action value '{action_value}' to the appropriate type for '{action_field}': {e}")
                        continue

                    # Set the value only if the conversion was successful or it's a string
                    if pd.notna(action_value) or isinstance(action_value, str):
                        df.loc[matches, action_field] = action_value
        except Exception as e:
            logger.error(f"Error applying rule '{rule}': {e}")

    return df

def apply_filters_vectorized(df, filter_semantics):
    if not filter_semantics:
        return df

    filtered_df = df.copy()
    for filter_condition in filter_semantics:
        try:
            if '>=' in filter_condition:
                field, condition = filter_condition.split('>=', 1)
                field = field.strip()
                condition = float(condition.strip()) if condition.strip().isdigit() else condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field].astype(type(condition)) >= condition]
            elif '>' in filter_condition:
                field, condition = filter_condition.split('>', 1)
                field = field.strip()
                condition = float(condition.strip()) if condition.strip().isdigit() else condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field].astype(type(condition)) > condition]
            elif '<=' in filter_condition:
                field, condition = filter_condition.split('<=', 1)
                field = field.strip()
                condition = float(condition.strip()) if condition.strip().isdigit() else condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field].astype(type(condition)) <= condition]
            elif '<' in filter_condition:
                field, condition = filter_condition.split('<', 1)
                field = field.strip()
                condition = float(condition.strip()) if condition.strip().isdigit() else condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field].astype(type(condition)) < condition]
            elif '!=' in filter_condition:
                field, condition = filter_condition.split('!=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field] != condition]
            elif '=' in filter_condition:
                field, condition = filter_condition.split('=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[field] == condition]
        except Exception as e:
            logger.error(f"Error applying filter '{filter_condition}': {e}")

    return filtered_df

def parse_condition(condition):
    operators = ['>=', '>', '<=', '<', '!=', '=']
    for op in operators:
        if op in condition:
            field, value = condition.split(op, 1)
            return field.strip(), op, value.strip()
    raise ValueError(f"Invalid condition: {condition}")

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
