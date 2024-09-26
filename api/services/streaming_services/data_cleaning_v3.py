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
            if path in df.columns:
                if 'timestamp' in key.lower():
                    result[key] = pd.to_datetime(df[path], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    result[key] = df[path]
    return result

def eval_condition(condition, df):
    condition = condition.strip()

    # Handling parentheses first (recursive evaluation of conditions inside parentheses)
    while '(' in condition and ')' in condition:
        inner_condition = re.search(r'\(([^()]+)\)', condition).group(1)
        inner_result = eval_condition(inner_condition, df)
        
        if isinstance(inner_result, pd.Series):
            result_str = f"@inner_result"
        else:
            result_str = str(inner_result)
        
        condition = condition.replace(f"({inner_condition})", result_str)

    # Splitting on OR first
    if 'OR' in condition:
        sub_conditions = condition.split('OR')
        combined_result = pd.Series([False] * len(df), index=df.index)
        for sub in sub_conditions:
            combined_result |= eval_condition(sub.strip(), df)
        return combined_result

    # Splitting on AND second
    if 'AND' in condition:
        sub_conditions = condition.split('AND')
        combined_result = pd.Series([True] * len(df), index=df.index)
        for sub in sub_conditions:
            combined_result &= eval_condition(sub.strip(), df)
        return combined_result

    # Now we have only simple comparisons (A > B, A < 10, etc.)
    field, operator, value = parse_condition(condition)

    if field in df.columns:
        if value in df.columns:
            value = df[value]  # Handle comparisons between columns
        else:
            try:
                value = float(value)
            except ValueError:
                pass  # Keep it as a string for comparison

        # Apply the comparison
        if operator == '>=':
            return df[field] >= value
        elif operator == '>':
            return df[field] > value
        elif operator == '<=':
            return df[field] <= value
        elif operator == '<':
            return df[field] < value
        elif operator == '!=':
            return df[field] != value
        elif operator == '=':
            return df[field] == value

    return pd.Series([False] * len(df), index=df.index)

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

                    if action_value in df.columns:
                        df.loc[matches, action_field] = df.loc[matches, action_value]  # Assign from another column
                    else:
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

                        if pd.notna(action_value) or isinstance(action_value, str):
                            df.loc[matches, action_field] = action_value

                # Apply ELSE action
                if else_part:
                    non_matches = ~matches
                    action_field, action_value = parse_then_action(else_part.strip())

                    if action_field not in df.columns:
                        df[action_field] = None

                    if action_value in df.columns:
                        df.loc[non_matches, action_field] = df.loc[non_matches, action_value]  # Assign from another column
                    else:
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

                        if pd.notna(action_value) or isinstance(action_value, str):
                            df.loc[non_matches, action_field] = action_value

        except Exception as e:
            logger.error(f"Error applying rule '{rule}': {e}")

    return df


def apply_filters_vectorized(df, filter_semantics):
    if not filter_semantics:
        return df

    filtered_df = df.copy()
    for filter_condition in filter_semantics:
        try:
            field, operator, condition = parse_condition(filter_condition)
            
            # Handle variable comparison (A > B)
            if condition in filtered_df.columns:
                condition = filtered_df[condition]
            else:
                try:
                    condition = float(condition)
                except ValueError:
                    pass  # Leave condition as string for comparison

            # Apply the filtering condition
            if operator == '>=':
                filtered_df = filtered_df[filtered_df[field] >= condition]
            elif operator == '>':
                filtered_df = filtered_df[filtered_df[field] > condition]
            elif operator == '<=':
                filtered_df = filtered_df[filtered_df[field] <= condition]
            elif operator == '<':
                filtered_df = filtered_df[filtered_df[field] < condition]
            elif operator == '!=':
                filtered_df = filtered_df[filtered_df[field] != condition]
            elif operator == '=':
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
