import argparse
import json
import logging
import sys
import time
from pathlib import Path

from lesson_loader import load_lessons_from_md, save_lessons_json


def generate(lessons_dir, output):
    lessons = load_lessons_from_md(lessons_dir)
    save_lessons_json(lessons, output)
    logging.info("Generated %s with %d lessons", output, len(lessons))
    return len(lessons)


def watch_mode(lessons_dir: str, output: str):
    """Start a filesystem watcher that regenerates JSON on markdown changes.

    This uses watchdog if available; otherwise falls back to single run.
    """
    try:
        from watchdog.observers import Observer
        from watchdog.events import PatternMatchingEventHandler
    except Exception:
        logging.warning("watchdog is not installed — running single generation instead.")
        generate(lessons_dir, output)
        return

    patterns = ["*.md", "*.markdown"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = False

    class _Handler(PatternMatchingEventHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def on_any_event(self, event):
            logging.info("Detected change (%s). Regenerating...", event.src_path)
            try:
                n = generate(lessons_dir, output)
                logging.info("Regenerated %s (%d lessons)", output, n)
            except Exception as e:
                logging.exception("Failed to regenerate lessons: %s", e)

    event_handler = _Handler(patterns=patterns, ignore_patterns=ignore_patterns,
                             ignore_directories=ignore_directories, case_sensitive=case_sensitive)
    observer = Observer()
    observer.schedule(event_handler, path=lessons_dir, recursive=True)
    observer.start()
    logging.info("Watching '%s' for changes. Press Ctrl+C to stop.", lessons_dir)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher...")
        observer.stop()
    observer.join()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--lessons-dir", default="lessons", help="Directory containing lesson .md files (default: lessons)")
    parser.add_argument("--output", default="generated_lessons.json", help="Output JSON file (default: generated_lessons.json)")
    parser.add_argument("--watch", action="store_true", help="Run in watch mode and regenerate on file changes (requires watchdog)")
    parser.add_argument("--log", default="info", help="Logging level (debug, info, warning, error)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    generate(args.lessons_dir, args.output)

    try:
        n = generate(args.lessons_dir, args.output)
    except Exception:
        logging.exception("Initial generation failed")
        sys.exit(1)

    if args.watch:
        watch_mode(args.lessons_dir, args.output)


if __name__ == "__main__":
    main()