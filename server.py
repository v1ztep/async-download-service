import argparse
import asyncio
import logging
import os
from functools import partial

import aiofiles
from aiohttp import web


def get_args():
    parser = argparse.ArgumentParser(
        description='Микросервис для скачивания файлов'
    )

    parser.add_argument('--turn_off_logs', type=bool, default=False,
                        help='Выключить логирование: default=False')
    parser.add_argument('--delayed_response', type=int, default=0,
                        help='Задержка ответа в секундах: default=0')
    parser.add_argument('--dest_folder', type=str, default='photos',
                        help='Путь к каталогу с фотографиями: default=photos')
    return parser.parse_args()


async def archivate(request, delayed_response, dest_folder):
    zip_args = ['zip', '-r', '-', '.']
    folder = request.match_info.get('archive_hash')
    if not os.path.exists(f'{dest_folder}/{folder}'):
        raise web.HTTPNotFound(
            text='Архив не существует или был удален'
        )
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; ' \
                                              'filename="archive.zip"'
    await response.prepare(request)

    subprocess = await asyncio.create_subprocess_exec(
        *zip_args,
        cwd=f'{dest_folder}/{folder}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        while True:
            stdout = await subprocess.stdout.read(n=512000)
            logging.debug('Sending archive chunk ...')
            if subprocess.stdout.at_eof():
                return response
            await response.write(stdout)
            if delayed_response:
                await asyncio.sleep(delayed_response)
    except asyncio.CancelledError:
        logging.error('Download was interrupted')
        raise
    except SystemExit as e:
        logging.error(f'SystemExit error: {e}')
        raise
    except Exception as exception:
        logging.error(f'Unexpected Exceptions: {exception}')
        raise
    finally:
        if subprocess.returncode is None:
            subprocess.kill()
            outs, errs = await subprocess.communicate()
        return response


async def handle_index_page(request):
    async with aiofiles.open(
            'index.html', mode='r', encoding='UTF-8'
    ) as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    args = get_args()
    logging.basicConfig(level=logging.INFO)
    if args.turn_off_logs:
        logging.disable(logging.CRITICAL)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get(
            '/archive/{archive_hash}/',
            partial(
                archivate,
                delayed_response=args.delayed_response,
                dest_folder=args.dest_folder
            )
        ),
    ])
    web.run_app(app)
