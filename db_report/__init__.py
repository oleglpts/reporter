import os
import pathlib


def copy_config():
    files = {
        'data/config.json': 'config.json',
        'data/locale/ru/LC_MESSAGES/db_report.mo': 'locale/ru/LC_MESSAGES/db_report.mo',
        'data/locale/en/LC_MESSAGES/db_report.mo': 'locale/en/LC_MESSAGES/db_report.mo',
        'data/reports/test_csv.json': 'reports/test_csv.json',
        'data/reports/test_postgresql_csv.json': 'reports/test_postgresql_csv.json',
        'data/reports/test_psycopg2_csv.json': 'reports/test_psycopg2_csv.json',
        'data/reports/test_sqlite3_csv.json': 'reports/test_sqlite3_csv.json',
        'data/reports/test_sqlite3_xls.json': 'reports/test_sqlite3_xls.json',
        'data/reports/test_sqlite3_xls.xml': 'reports/test_sqlite3_xls.xml',
        'data/reports/test_xls.json': 'reports/test_xls.json',
        'data/reports/test_tab.json': 'reports/test_tab.json',
        'data/reports/test_json.json': 'reports/test_json.json',
        'data/reports/test_xls.xml': 'reports/test_xls.xml',
        'data/test/chinook.sqlite': 'test/chinook.sqlite',
        'data/test/get_data_xls.py': 'test/get_data_xls.py',
        'data/test/get_data_csv.py': 'test/get_data_csv.py',
        'data/test/get_data_tab.py': 'test/get_data_tab.py',
        'data/test/get_data_json.py': 'test/get_data_json.py',
        'test/test.sh': 'test.sh',
        'test/test_clean.sh': 'test_clean.sh'
    }
    for file_name in files:
        path = pathlib.Path(os.getenv('HOME'), '.' + __name__, files[file_name])
        path.parent.mkdir(parents=True, exist_ok=True)
        open(str(path), 'wb').write(open(pathlib.Path(__name__, file_name), 'rb').read())
