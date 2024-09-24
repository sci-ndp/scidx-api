import pandas as pd
import logging
import time
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


def apply_filters_vectorized(df, filter_semantics):
    if not filter_semantics:
        return df

    # logger.info("DataFrame before filtering:\n%s", df.head())  
    
    for filter_condition in filter_semantics:
        try:
            if '>=' in filter_condition:
                field, condition = filter_condition.split('>=', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) >= condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '>' in filter_condition:
                field, condition = filter_condition.split('>', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) > condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '<=' in filter_condition:
                field, condition = filter_condition.split('<=', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) <= condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '<' in filter_condition:
                field, condition = filter_condition.split('<', 1)
                field = field.strip()
                condition = float(condition.strip())
                if field in df.columns:
                    df = df[df[field].astype(float) < condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '!=' in filter_condition:
                field, condition = filter_condition.split('!=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in df.columns:
                    try:
                        df = df[df[field].astype(float) != float(condition)]
                    except ValueError:
                        df = df[df[field] != condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
            elif '=' in filter_condition:
                field, condition = filter_condition.split('=', 1)
                field = field.strip()
                condition = condition.strip()
                if field in df.columns:
                    try:
                        df = df[df[field].astype(float) == float(condition)]
                    except ValueError:
                        df = df[df[field] == condition]
                else:
                    return pd.DataFrame()  # Return empty DataFrame if field is missing
        except Exception as e:
            logger.error(f"Error applying filter '{filter_condition}': {e}")

    return df



async def process_and_send_data(messages, mapping, stream, send_data, buffer_lock, loop, filter_semantics, additional_info=None):
    async with buffer_lock:
        df = pd.DataFrame(messages)
        mapped_data = mapped_values_vectorized(mapping, df)
        filtered_data = apply_filters_vectorized(mapped_data, filter_semantics)
        if not filtered_data.empty:
            if additional_info:
                if isinstance(additional_info, dict):
                    stream.extras.update(additional_info)
                elif isinstance(additional_info, str):
                    stream.extras['additional_info'] = additional_info
                else:
                    stream.extras['additional_info'] = str(additional_info)
            # logger.info("Filtered DataFrame:\n%s", filtered_data.head())
            await send_data(filtered_data, stream, loop)
        else:
            pass
            # logger.info("No data after filtering")
