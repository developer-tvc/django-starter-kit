import os
from dotenv import load_dotenv


load_dotenv()


def get_env_variable(var_name: str) -> str:
    """Utility function to get an environment variable or raise a ValueError"""
    value = os.getenv(var_name)
    print(value,"-------------------")
    if value is None:
        raise ValueError(f"{var_name} Environment variable not set")
    return value



def validate_file_path(file_path):
    """Validates if the given file path exists."""
    if file_path and not os.path.exists(file_path):
        raise RuntimeError(f"File path '{file_path}' does not exist.")
    return file_path