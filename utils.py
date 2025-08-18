import secrets

def generate_api_key():
    return secrets.token_hex(16)

def get_serial_from_content(json_content):
    if not isinstance(json_content, list):
        return None
    try:
        first_dict = json_content[0]
        if isinstance(first_dict, dict):
            return first_dict.get("Serial")
    except Exception:
        return None
    return None

