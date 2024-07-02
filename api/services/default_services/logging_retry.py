import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def log_retry_attempt(retry_state):
    logging.warning(f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()}")