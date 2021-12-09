import subprocess


def main():
    zip_args = ['zip', '-r', '-', 'photos/']
    with open('archive.zip', "w+b") as file:
        bytes = bytearray(file.read())
        bytes.extend(subprocess.check_output(zip_args))
        file.seek(0)
        file.write(bytes)


if __name__ == '__main__':
    main()
