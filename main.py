import asyncio


async def archivate(folder='photos/', filename='archive.zip'):
    zip_args = f'-r - {folder}' # экранировать https://docs.python.org/3.7/library/shlex.html#shlex.quote
    with open(filename, "w+b") as file:
        bytes = bytearray(file.read())
        subprocess = await asyncio.create_subprocess_shell(
            f'zip {zip_args}',
            stdout=asyncio.subprocess.PIPE
        )
        while True:
            stdout = await subprocess.stdout.read(n=512000)
            bytes.extend(stdout)
            file.seek(0)
            file.write(bytes)
            if subprocess.stdout.at_eof():
                break


def main():
    asyncio.run(archivate())


if __name__ == '__main__':
    main()
