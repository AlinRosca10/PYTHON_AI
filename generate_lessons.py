import argparse
import json
import logging
import sys
import time
from pathlib import Path

from lesson_loader import load_lessons_from_md, save_lessons_json


# ==========================================================
# Core generator
# ==========================================================

def generate(lessons_dir: Path, output: Path) -> int:
    """Load lessons from directory and write them into a JSON file."""
    start = time.time()

    lessons = load_lessons_from_md(lessons_dir)
    save_lessons_json(lessons, output)

    logging.info("Generated %s with %d lessons (%.1f ms)",
                 output, len(lessons), (time.time() - start) * 1000)

    return len(lessons)


# ==========================================================
# Watch mode (optional, using watchdog)
# ==========================================================

def watch_mode(lessons_dir: Path, output: Path):
    """Watch filesystem for changes in .md files and regenerate JSON."""

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except Exception:
        logging.warning("watchdog is not installed — running single generation only.")
        generate(lessons_dir, output)
        return

    class Handler(FileSystemEventHandler):
        """Handles modifications to markdown files with debounce."""
        debounce_interval = 0.3
        last_run = 0

        def on_any_event(self, event):
            # Only regenerate on .md changes
            if not event.src_path.endswith((".md", ".markdown")):
                return

            now = time.time()
            if now - self.last_run < self.debounce_interval:
                return  # debounce: ignore rapid duplicate events

            self.last_run = now

            logging.info("Detected change in %s — regenerating...", event.src_path)
            try:
                generate(lessons_dir, output)
            except Exception:
                logging.exception("Regeneration failed!")

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, str(lessons_dir), recursive=True)
    observer.start()

    logging.info("Watching '%s' for changes... Press Ctrl+C to stop.", lessons_dir)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher...")
    finally:
        observer.stop()
        observer.join()


# ==========================================================
# CLI entry point
# ==========================================================

def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate lessons JSON from .md files.")
    parser.add_argument("--lessons-dir", default="lessons",
                        help="Directory containing markdown lessons (default: lessons)")
    parser.add_argument("--output", default="generated_lessons.json",
                        help="JSON file to generate (default: generated_lessons.json)")
    parser.add_argument("--watch", action="store_true",
                        help="Watch mode — regenerate on file changes (requires watchdog)")
    parser.add_argument("--log", default="info",
                        help="Logging level: debug/info/warning/error (default: info)")

    args = parser.parse_args(argv)

    # Configure logging
    logging.basicConfig(level=args.log.upper(), format="%(levelname)s: %(message)s")

    lessons_dir = Path(args.lessons_dir)
    output = Path(args.output)

    # Initial generation
    try:
        count = generate(lessons_dir, output)
        logging.info("Initial generation complete (%d lessons).", count)
    except Exception:
        logging.exception("Initial generation failed.")
        sys.exit(1)

    # Watch mode
    if args.watch:
        watch_mode(lessons_dir, output)


if __name__ == "__main__":
    main()