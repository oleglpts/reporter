# _*_ coding: utf-8 _*_

import xlwt
import pyodbc

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

        def compute_all():
            """

            Compute subtotals and totals

            """

            def suppress_field(ind):
                """

                Suppress field

                :param ind: current row
                :type ind: int
                :return: new current row
                :rtype: int

                """
                while ind < len(self._rows) and self._rows[ind][num] == work:
                    stop = False
                    for field_name in field_numbers:
                        if field_name == field[0]:
                            continue
                        if self._rows[ind][field_numbers[field_name]] != '':
                            stop = True
                    if stop:
                        break
                    row = [self._rows[ind][p] for p in range(len(self._rows[0]))]
                    row[num] = ''
                    self._rows[ind] = tuple(row)
                    ind += 1
                return ind

            for num, field in enumerate(self._conn.description):
                field_numbers[field[0]] = num
                if totals and field[0] in totals:
                    totals[field[0]] = self._rows[0][num]
                if field[0] in suppress or field[0] in total or field[0] in subtotal:
                    i, work = 1, self._rows[0][num]
                    while i < len(self._rows):
                        if totals and field[0] in totals:
                            totals[field[0]] += \
                                self._rows[i][num] if isinstance(
                                    self._rows[i][num], float) or isinstance(self._rows[i][num], int) else 0.0
                        if field[0] in suppress:
                            i = suppress_field(i)
                            subtotal_rows[field[0]].append(i)
                            skip = self._get_int(self._get_attr(node, "skip", '0'))
                            if i < len(self._rows):
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
            if total:
                set_totals()
            if subtotal:
                compute_subtotals()

        def set_totals():
            """

            Set totals values

            """
            skip_totals = self._get_int(self._get_attr(node, "skip_totals", '1'))
            y = ['' for _ in range(len(self._rows[0]))]
            for f in range(skip_totals):
                self._rows.append(tuple(y))
            y[0] = '<b>Total:'
            for x in totals:
                y[field_numbers[x]] = '<b>%s' % totals[x]
            self._rows.append(tuple(y))

        def compute_subtotals():
            """

            Compute subtotals

            """
            for suppress_num, suppress_field in enumerate(suppress):
                for subtotal_field in subtotal:
                    low_limit = 0
                    for high_limit in subtotal_rows[suppress_field]:
                        sum_subtotal = 0.0
                        for k in range(low_limit, high_limit):
                            value = self._rows[k][field_numbers[subtotal_field]]
                            sum_subtotal += value if isinstance(value, float) or isinstance(value, int) else 0.0
                        low_limit = high_limit + len(suppress) - 1
                        in_subtotals = high_limit + len(suppress) - suppress_num - 1 in subtotals
                        row_num = high_limit + len(suppress) - suppress_num - 1
                        from_rows = [self._rows[row_num][x] for x in range(len(self._rows[0]))]
                        seq = subtotals[row_num] if in_subtotals else from_rows
                        seq[field_numbers[subtotal_field]] = '<b>%s' % sum_subtotal
                        seq[field_numbers[suppress_field]] = '<b>Subtotal:'
                        subtotals[high_limit + len(suppress) - suppress_num - 1] = seq

        request = node.text
        if request is None:
            self._rows = [(0,)]
            return
        try:
            self._conn.execute(request)
        except pyodbc.Error as e:
            self._logger.error("database error: %s" % str(e))
            self._logger.error('hint: incorrect sql or sql parameter?')
            exit(1)
        self._rows = self._conn.fetchall()
        suppress = self._string_to_list(self._get_attr(node, "suppress", ''))
        subtotal = self._string_to_list(self._get_attr(node, "subtotal", ''))
        total = self._string_to_list(self._get_attr(node, "total", ''))
        totals = {name: 0.0 for name in total}
        subtotals = {}
        field_numbers = {}
        subtotal_rows = {x: [] for x in suppress}
        if (suppress or total or subtotal) and len(self._rows) > 1:
            compute_all()
        for x in subtotals:
            self._rows[x] = subtotals[x]
        if len(self._rows) > self._rows_max:
            self._rows_max = len(self._rows)

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
