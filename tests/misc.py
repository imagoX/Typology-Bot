from config import BOT_TOKEN

def format_response(text):
    """
    Formats the bot's response with a custom prefix.
    
    Args:
    text (str): The original text to be sent back to the user.
    
    Returns:
    str: The formatted response text.
    """
    return f": {text}"
