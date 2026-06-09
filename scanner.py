from pathlib import Path
from datetime import datetime


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".xlsx",
    ".csv"
}


class FileScanner:
    def __init__(self, root_directory: str):
        self.root_directory = Path(root_directory)

    def scan(self):
        """
        Рекурсивно сканирует каталог и возвращает список файлов.
        """

        files = []

        for file_path in self.root_directory.rglob("*"):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            try:
                stat = file_path.stat()

                files.append({
                    "name": file_path.name,
                    "path": str(file_path.resolve()),
                    "extension": file_path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(
                        stat.st_ctime
                    ).isoformat(),
                    "modified_at": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat()
                })

            except Exception as e:
                print(f"[ERROR] {file_path}: {e}")

        return files


if __name__ == "__main__":

    scanner = FileScanner("uploads")

    result = scanner.scan()

    print(f"Found files: {len(result)}")

    for file_info in result:
        print(file_info)