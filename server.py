import asyncio
import logging
import os

import aiofiles
from aiohttp import web


async def archivate(request):
    zip_args = ['zip', '-r', '-', '.']
    folder = request.match_info.get('archive_hash')
    if not os.path.exists(f'photos/{folder}'):
        raise web.HTTPNotFound(
            text='Архив не существует или был удален'
        )
    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'attachment; ' \
                                              'filename="archive.zip"'
    await response.prepare(request)

    subprocess = await asyncio.create_subprocess_exec(
        *zip_args,
        cwd=f'photos/{folder}',
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
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
