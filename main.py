import asyncio


async def archivate(folder='test/', filename='archive.zip'):
    zip_args = ['zip', '-r', '-', '.']
    subprocess = await asyncio.create_subprocess_exec(
        *zip_args,
        cwd=folder,
        stdout=asyncio.subprocess.PIPE
    )
    while True:
        with open(filename, "a+b") as file:
            stdout = await subprocess.stdout.read(n=512000)
            file.write(stdout)
        if subprocess.stdout.at_eof():
            break


def main():
    asyncio.run(archivate())


if __name__ == '__main__':
    main()
