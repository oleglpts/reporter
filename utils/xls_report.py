# _*_ coding: utf-8 _*_

import xlwt
import psycopg2

from utils.base_xls_report import BaseXLSReport

"""

Генерация отчётов на основании XML-описания и вывод их в .xls-файл

"""


class XLSReport(BaseXLSReport):
    """

    "Public" методы

    """
    """

    Конструктор

    """

    def __init__(self, param):
        """
        Конструктор

        Список параметров должен содержать как минимум параметры:
        host, port, database, user, password, xml, sql, title
        :param param: параметры командной строки
        :type param: dict
        """
        BaseXLSReport.__init__(self, param)

    """

    "Protected" методы

    """
    """

    Установка параметров, подставляемых из командной строки

    """

    def _set_parameters(self):
        """
        Установка параметров, подставляемых
        из командной строки
        """
        self._parameters = self._param['parameters']

    """

    Установка методов обработки тегов

    """
    def _set_tags(self):
        """
        Установка методов обработки тегов
        """
        self._tags = {
            "report": self.get_report,                      # <report>
            "name": self.get_name,                          # <name>
            "literal": self.get_literal,                    # <literal>
            "groupliteral": self.get_groupliteral,          # <groupliteral>
            "sql": self.get_sql,                            # <sql>
            "request": self.get_request,                    # <request>
            "group": self.get_group,                        # <group>
            "field": self.get_field,                        # <field>
            "formula": self.get_formula,                    # <formula>
            "styledef": self.get_styledef                   # <styledef>
        }

    """

    Табличные "protected" методы

    """
    """

    Обработка тега <report>

    """

    def get_report(self, node):
        """
        Обработка тега <report>

        # :param node: элемент дерева разбора, содержащий тег
        # :type node: _Element
        """
        self._ws = None                                     # текущая вкладка .xls-файла
        self._step = 1                                      # шаг отображения строки текущего отчёта
        self._curr = 0                                      # текущая строка отчёта
        self._max = -1                                      # максимальный номер строки относительно начала отчёта
        self._field = 0                                     # текущее поле SQL-запроса
        self._rows_max = 0                                  # максимальное количество строк в запросе отчёта

    """

    Обработка тега <styledef>

    """

    def get_styledef(self, node):
        """
        Обработка тега <styledef>

        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        self._styles[self._get_attr(node, "name", "Normal")]\
            = node.text                                     # просто добавляется стиль в словарь

    """

    Обработка тега <literal>

    """
    def get_literal(self, node):
        """
        Обработка тега <literal>

        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        row = self._get_int(self._get_attr(node, "row"))    # строка в файле
        col = self._get_int(self._get_attr(node, "col"))    # столбец в файле
        self._ws.write(row + self._curr, col, node.text,    # запись в файл
                       self._get_style(node))               # со стилем

    """

    Обработка тега <name>

    """

    def get_name(self, node):
        """
        Обработка тега <name>

        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        sheet_name = node.text if node.text is not None \
            else "Sheet%d" % self._sheet                    # имя отчёта
        self._sheet += 1                                    # текущая вкладка
        self._ws = self._wb.add_sheet(sheet_name)           # добавить новую вкладку

    """

    Обработка тега <sql>

    """

    def get_sql(self, node):
        """
        Обработка тега <sql>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        if self._get_attr(node, "cycle", "no") == "no":     # если запрос не циклический
            self._curr = self._max+1                        # подогнать текущую строку
        self._field = 0                                     # обнулить текущее поле
        self._rows = [(0,)]

    """

    Обработка тега <request>

    """

    def get_request(self, node):
        """
        Обработка тега <request>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        request = node.text                                 # запрос
        if request is not None:
            try:                                                # пробуем
                self._conn.execute(request)                     # выполнить запрос
            except psycopg2.Error as e:                         # похоже
                print("Hint: incorrect --sql-parameter?")       # на ошибку,
                print("Database error: %s" % str(e))            # обработать
                exit(1)                                         # и выйьт
            self._rows = self._conn.fetchall()                  # вытащить результат
            suppress = [x.strip() for x in self._get_attr(node, "suppress", '').split(',')]
            if suppress == ['']:
                suppress = []
            subtotal = [x.strip() for x in self._get_attr(node, "subtotal", '').split(',')]
            if subtotal == ['']:
                subtotal = []
            total = [x.strip() for x in self._get_attr(node, "total", '').split(',')]
            if total == ['']:
                total = []
            totals = {name: 0.0 for name in total}
            subtotals = {}
            field_numbers = {}
            subtotal_rows = {x: [] for x in suppress}
            if (suppress or total or subtotal) and len(self._rows) > 1:
                i = 0
                for num, field in enumerate(self._conn.description):
                    field_numbers[field[0]] = num
                    if totals and field[0] in totals:
                        totals[field[0]] = self._rows[0][num]
                    if field[0] in suppress or field[0] in total or field[0] in subtotal:
                        i, work = 1, self._rows[0][num]
                        while i < len(self._rows):
                            if totals and field[0] in totals:
                                totals[field[0]] += self._rows[i][num] if isinstance(self._rows[i][num], float) else 0.0
                            if field[0] in suppress:
                                while self._rows[i][num] == work and i < len(self._rows):
                                    nn = [self._rows[i][p] for p in range(len(self._rows[0]))]
                                    nn[num] = ''
                                    self._rows[i] = tuple(nn)
                                    i += 1
                                subtotal_rows[field[0]].append(i)
                                skip = self._get_int(self._get_attr(node, "skip", '0'))
                                for _ in range(skip):
                                    self._rows.insert(i, tuple('' for _ in range(len(self._rows[i]))))
                                    for y in subtotal_rows:
                                        for z in range(len(subtotal_rows[y])):
                                            if subtotal_rows[y][z] > i:
                                                subtotal_rows[y][z] += 1
                                i += skip
                                work = self._rows[i][num]
                                while work == '' and i < len(self._rows):
                                    i += 1
                                    work = self._rows[i][num]

                            i += 1
                for x in subtotal_rows:
                    subtotal_rows[x].append(i)
                if total:
                    skip_totals = self._get_int(self._get_attr(node, "skip_totals", '1'))
                    y = ['' for _ in range(len(self._rows[0]))]
                    for f in range(skip_totals):
                        self._rows.append(tuple(y))
                    y[0] = '<b>Total:'
                    for x in totals:
                        y[field_numbers[x]] = '<b>%s' % totals[x]
                    self._rows.append(tuple(y))
                if subtotal:
                    for m, sp in enumerate(suppress):
                        for fl in subtotal:
                            i = 0
                            for j in subtotal_rows[sp]:
                                s = 0.0
                                for k in range(i, j):
                                    s += self._rows[k][field_numbers[fl]] if isinstance(self._rows[k][field_numbers[fl]], float) else 0.0
                                i = j + len(suppress) - 1
                                if j + len(suppress) - m - 1 in subtotals:
                                    y = subtotals[j + len(suppress) - m - 1]
                                else:
                                    y = [self._rows[j + len(suppress) - m - 1][x] for x in range(len(self._rows[0]))]
                                y[field_numbers[fl]] = '<b>%s' % s
                                y[field_numbers[sp]] = '<b>Subtotal:'
                                subtotals[j + len(suppress) - m - 1] = y
            for x in subtotals:
                self._rows[x] = subtotals[x]
            if len(self._rows) > self._rows_max:                # скорректировать
                self._rows_max = len(self._rows)                # максимльное количество
        else:
            self._rows = [(0,)]

    """

    Обработка тега <group>

    """

    def get_group(self, node):
        """
        Обработка тега <group>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        self._step = self._get_int(                         # установить шаг
            self._get_attr(node, "step", "1"))              # вывода строк отчёта

    """

    Обработка тега <field>

    """

    def get_field(self, node):
        """
        Обработка тега <field>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        row = self._get_int(self._get_attr(node, "row")) + self._curr
        col = self._get_int(self._get_attr(node, "col"))
        width = self._get_attr(node, "width")
        if width.isdigit():
            self._ws.col(col).width = self._get_int(width)
        if node.attrib["header"] == "yes":
            self._ws.write(row, col, self._get_attr(node, "name"))
        else:
            row -= self._step
        for i in range(len(self._rows)):
            row += self._step
            if self._rows[i][self._field]:
                value = self._rows[i][self._field]
                try:
                    value = float(value)
                except ValueError:
                    pass
            else:
                value = ''
            append = ''
            if str(value).startswith('<b>'):
                value = str(value)[3:]
                if value.isnumeric():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                append = 'font: bold True;'
            self._ws.write(row, col, value, self._get_style(node, append))
        if row > self._max:
            self._max = row
        self._field += 1

    """

    Обработка тега <formula>

    """

    def get_formula(self, node):
        """
        Обработка тега <formula>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        row = self._get_int(self._get_attr(node, "row")) + self._curr
        col = self._get_int(self._get_attr(node, "col"))
        cycle = self._get_int(self._get_attr(node, "cycle", '0'))
        if self._get_attr(node, "header") == "yes":
            self._ws.write(row, col, self._get_attr(node, "name"))
        else:
            row -= self._step
        for i in range(len(self._rows) if not cycle else cycle):
            row += self._step
            formula = node.text
            formula = formula.replace("{{cs}}", str(row + 1)). \
                replace("{{ss}}", str(self._curr + i * self._step + 1)). \
                replace("{{ds}}", str(row))
            self._ws.write(row, col, xlwt.Formula(formula), self._get_style(node))
        if row > self._max:
            self._max = row

    """

    Обработка тега <groupliteral>

    """

    def get_groupliteral(self, node):
        """
        Обработка тега <groupliteral>
        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        """
        row = self._get_int(self._get_attr(node, "row")) + self._curr
        col = self._get_int(self._get_attr(node, "col"))
        if self._get_attr(node, "header") == "yes":
            self._ws.write(row, col, self._get_attr(node, "name"))
        else:
            row -= self._step
        for i in range(self._rows_max):
            row += self._step
            value = node.text
            value = value.replace("{{cs}}", str(row + 1)). \
                replace("{{ss}}", str(self._curr + i * self._step + 1)). \
                replace("{{ds}}", str(row))
            try:
                value = float(value)
            except ValueError:
                pass
            self._ws.write(row, col, value, self._get_style(node))
        if row > self._max:
            self._max = row
