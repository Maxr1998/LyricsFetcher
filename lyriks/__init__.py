import os
from os import path
from pathlib import Path
from sys import stderr

from .cli import parse_arguments
from .lyrics_fetcher import LyricsFetcher


def main():
    args = parse_arguments()

    collection_path = args.path
    report_path: Path = args.report

    # Normalize and validate report path
    if report_path:
        report_path = report_path.expanduser().absolute()
        if report_path.is_dir():
            report_path = report_path / 'report.html'
        if not report_path.parent.exists():
            print(f'Error: directory \'{report_path.parent}\' does not exist', file=stderr)
            exit(2)

    fetcher = LyricsFetcher(args.dry_run, args.force)

    for root_dir, dirs, files in os.walk(collection_path, topdown=True):
        if path.exists(path.join(root_dir, '.nolyrics')):
            dirs.clear()
            continue

        for file in files:
            if file.lower().endswith('.flac') or file.lower().endswith('.mp3'):
                fetcher.fetch_lyrics(path.join(root_dir, file))

    if report_path:
        try:
            fetcher.write_report(report_path)
        except OSError:
            print(f'Error: could not write report to \'{report_path}\'', file=stderr)
            exit(2)
