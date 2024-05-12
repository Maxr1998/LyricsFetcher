class Lyrics:
    def __init__(self, lines, is_timed):
        self._lines = lines
        self.is_timed = is_timed

    def write_to_file(self, path: str):
        with open(path, 'w') as f:
            f.writelines(self._lines)

    @staticmethod
    def timed(lyrics_dict: dict[str, str]) -> 'Lyrics':
        return Lyrics(_convert_to_lrc(lyrics_dict), is_timed=True)

    @staticmethod
    def static(lyrics: list[str]) -> 'Lyrics':
        return Lyrics([line + '\n' for line in lyrics], is_timed=False)


def _convert_to_lrc(lyrics_dict: dict[str, str]) -> list[str]:
    """Takes a dict of millis/lines, and converts it to the lrc format."""
    lyrics_dict = {int(timestamp): line.strip() for timestamp, line in lyrics_dict.items()}
    sorted_lines = sorted(lyrics_dict.items())
    formatted_lines = [f'{_millis_to_lrc_timestamp(timestamp)}{line}\n' for timestamp, line in sorted_lines]
    return formatted_lines


def _millis_to_lrc_timestamp(timestamp: int) -> str:
    minutes = timestamp // 60000
    seconds = (timestamp % 60000) // 1000
    centis = (timestamp % 1000) // 10
    return f'[{minutes:02d}:{seconds:02d}:{centis:02d}]'
