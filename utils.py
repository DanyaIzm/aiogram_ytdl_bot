def convert_str_to_seconds(value: str) -> int:
    minutes, seconds = map(int, value.split(":"))

    return minutes * 60 + seconds
