import csv
from pathlib import Path

from docx import Document
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path("test_catalog")

# Кандидаты на шрифт с поддержкой кириллицы (Windows / Linux / macOS).
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def _register_cyrillic_font():
    """Регистрирует первый найденный TTF с кириллицей. Возвращает имя шрифта или None."""
    for path in _FONT_CANDIDATES:
        if Path(path).exists():
            try:
                pdfmetrics.registerFont(TTFont("CyrFont", path))
                return "CyrFont"
            except Exception:
                continue
    return None


def make_txt(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def make_docx(path: Path, paragraphs):
    path.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    for p in paragraphs:
        document.add_paragraph(p)
    document.save(path)


def make_xlsx(path: Path, dataframe: pd.DataFrame):
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_excel(path, index=False)


def make_pdf(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont(_register_cyrillic_font() or "Helvetica", 12)
    y = 800
    for line in lines:
        c.drawString(50, y, line)
        y -= 24
    c.save()


def build():

    # --- Критический: журнал инцидента (несанкционированный доступ) ---
    make_txt(
        ROOT / "incidents" / "incident_access.txt",
        "Журнал инцидента: несанкционированный доступ к сервису.\n"
        "Скомпрометированная учётная запись:\n"
        "Логин: service_admin\n"
        "Пароль: Qw!2024_root\n"
        "Источник подключения: 203.0.113.45\n"
        "Перехваченный токен сессии: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTkifQ.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk\n"
        "Ключ API платёжного шлюза: sk-LIVEabcdefghij1234567890XYZ\n"
        "Уведомления об инцидентах: soc@corp-test.local\n"
    )

    # --- Критический: утечка учётных данных (.txt) ---
    make_txt(
        ROOT / "perepiska" / "leak_credentials.txt",
        "Сервер: 192.168.10.5\n"
        "Резервный сервер: 10.0.0.1\n"
        "Логин: admin\n"
        "Пароль: qwerty123\n"
        "Резервный пароль: P@ssw0rd2024\n"
        "email для уведомлений: alerts@corp-test.local\n"
        "Панель управления: http://192.168.10.5:8080/admin\n"
    )

    # --- Высокий: лог переписки (.csv) ---
    make_csv(
        ROOT / "perepiska" / "chat_log.csv",
        [
            ["time", "user", "message"],
            ["10:00", "bob", "пиши мне на bob@mail-test.io"],
            ["10:05", "alice", "файлы тут https://files-test.io/share"],
            ["10:10", "bob", "пароль: secret2024"],
        ],
    )

    # --- Высокий: отчёт с хешами (.docx) ---
    make_docx(
        ROOT / "otchety" / "otchet.docx",
        [
            "Технический отчёт по исследованию носителя.",
            "Хеш файла (MD5): d41d8cd98f00b204e9800998ecf8427e",
            "SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "IP источника подключения: 8.8.8.8",
            "Ответственный: expert@forensic-test.org",
        ],
    )

    # --- Средний: таблица контактов (.xlsx) ---
    make_xlsx(
        ROOT / "otchety" / "tablica.xlsx",
        pd.DataFrame(
            {
                "ФИО": ["Иванов И.И.", "Петров П.П."],
                "Email": ["ivanov@test-co.ru", "petrov@test-co.ru"],
                "Телефон": ["+7 999 111 22 33", "8 916 222 33 44"],
            }
        ),
    )

    # --- Высокий: скан документа (.pdf) ---
    make_pdf(
        ROOT / "skany" / "scan_dokumenta.pdf",
        [
            "Конфиденциально.",
            "Доступ к системе: http://10.20.30.40/panel",
            "IP: 10.20.30.40",
            "Пароль администратора: Adm1n!2024",
            "Контакт: it@secure-test.net",
        ],
    )

    # --- Средний: договор (.txt) ---
    make_txt(
        ROOT / "dogovor.txt",
        "ДОГОВОР № 12/2025\n"
        "Сторона А: ООО «Ромашка», контактное лицо ivanov@romashka-test.ru,\n"
        "тел. +7 495 123 45 67. Сайт компании: romashka-test.ru\n"
        "Предмет договора: оказание консультационных услуг.\n",
    )

    # --- Низкий: пустая записка без артефактов (.txt) ---
    make_txt(
        ROOT / "pustaya_zapiska.txt",
        "Памятка: проверить материалы по делу. "
        "Ничего конфиденциального здесь нет.\n",
    )


if __name__ == "__main__":

    build()

    created = sorted(
        p for p in ROOT.rglob("*") if p.is_file()
    )

    print(f"Создан тестовый каталог: {ROOT.resolve()}")
    print(f"Файлов: {len(created)}")
    for p in created:
        print("  ", p.relative_to(ROOT))