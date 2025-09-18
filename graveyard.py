import argparse
import functools
import http.server
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

import combustache
import watchdog
import watchdog.events
import watchdog.observers

template_path = Path('./template.html')
posts_path = Path('./posts/')
assets_path = Path('./assets/')
dist_path = Path('./.dist/')
index_path = dist_path / 'index.html'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('graveyard').setLevel(os.environ.get('LOGGING', 'INFO'))

logger = logging.getLogger('graveyard')
http_logger = logging.getLogger('graveyard.http')


def render_index() -> str:
    logger.debug(f'Loaded template: {template_path}')
    template = combustache.Template(template_path.read_text())
    logger.debug('Started rendering')

    posts = []
    for post_file in posts_path.iterdir():
        logger.debug(f'Processing: {post_file}')
        date = post_file.name[:10]
        content = post_file.read_text()
        posts.append({'date': date, 'content': content})
    posts.sort(key=lambda x: x['date'], reverse=True)

    prev_post_date = datetime.now()
    for i, post in enumerate(posts):
        curr_post_date = datetime.fromisoformat(post['date'])

        post['id'] = len(posts) - i
        post['days'] = (prev_post_date - curr_post_date).days + 1

        prev_post_date = curr_post_date

    data = {'posts': posts}
    render = template.render(data)
    logger.debug('Ended rendering')
    return render


class LoggingHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        message = (format % args).translate(self._control_char_table)  # pyright: ignore[reportAttributeAccessIssue]
        http_logger.info(message)


def serve(addr: str, port: int, directory: str) -> None:
    MyHandler = functools.partial(
        LoggingHTTPRequestHandler, directory=str(directory)
    )
    with http.server.ThreadingHTTPServer((addr, port), MyHandler) as httpd:
        httpd.serve_forever()


class MyHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.on_created = self.on_modified = self.on_moved = (
            self.on_deleted
        ) = self.handle

    def handle(self, event: watchdog.events.FileSystemEvent) -> None:
        if event.is_directory:
            return
        logger.info(f'Rebuilding: {event.src_path} {event.event_type}')
        index_path.write_text(render_index())


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-w',
        '--watch',
        nargs='?',
        const='localhost:5000',
        default=None,
        help="watcher mode (serves by default on 'localhost:5000')",
    )
    args = parser.parse_args(argv)

    logger.info(f'Removing dist: {dist_path}')
    shutil.rmtree(dist_path, ignore_errors=True)
    dist_path.mkdir(parents=True)
    link_path = assets_path.relative_to(dist_path, walk_up=True)
    logger.info(
        f'Linking assets: {dist_path / assets_path} to {dist_path / link_path}'
    )
    (dist_path / assets_path).symlink_to(link_path, target_is_directory=True)
    logger.info(f'Building {index_path}')
    index_path.write_text(render_index())

    if not args.watch:
        sys.exit(0)

    addr, _, port = args.watch.partition(':')

    observer = watchdog.observers.Observer()
    handler = MyHandler()
    observer.schedule(handler, str(posts_path))
    observer.schedule(handler, str(template_path))
    observer.start()
    logger.info(f'Watching: {addr}:{port}')
    try:
        serve(addr, int(port), str(dist_path))
    except KeyboardInterrupt:
        logger.info('Exiting')
    finally:
        observer.stop()
        observer.join()


if __name__ == '__main__':
    main(None)
