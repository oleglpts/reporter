# _*_ coding: utf-8 _*_

import re
import abc
import xlwt
from xlwt.Style import XFStyle
from utils.base_xml import BaseXML

"""

Получение состава групп

"""


class Groups(BaseXML):

    def __init__(self, param):
        """
        Конструктор

        :param param: параметры класса
        :type param: dict
        """
        BaseXML.__init__(self, param)
        self.groups = {}

    def _set_tags(self):
        """
        Установка методов для обработки тегов
        """
        self._tags = {
            "group": self._get_group
        }

    def _replace_param(self, xml):
        """
        Замены параметров в исходном файле

        В данном случае, ничего не делает
        :param xml: исходный XML-файл
        :return: XML-файл с подстановками
        :rtype: str
        """
        return xml

    def _get_group(self, node):
        """
        Обработка тега <group>

        :param node: текущий элемент дерева разбора
        :type node: _Element
        """
        nm = self._get_attr(node, "name")
        value = re.sub("^\s+|\n|\r|\s+$", '', node.text).split(',')
        self.groups[nm] = value


"""

Составление книги из XML-описаний отчётов

"""


class ReportXML:
    """
    "Public" методы
    """

    def __init__(self, filename, reports):
        """
        Конструктор

        :param filename: имя файла
        :type filename str
        :param reports: список имён XML-описаний отчётов
        :type reports: list
        """
        self._file = open(filename, "w")                    # открываем на запись
        self._file.write(                                   # пишем
            "<?xml version='1.0' encoding='utf-8'?>\n"      # заголовок
            "<book>\n"                                      # XML-файла
        )                                                   # и открываем книгу
        self._report_xml = self.report = None               # инициализация переменных
        self._report_num = -1                               # текущий номер отчёта
        self._report_type = 0                               # текущий тип отчёта
        self._reports = reports                             # список отчётов
        self._last_report = False                           # признак последнего отчёта
        self.parm_cnt = self.title_cnt = 0                  # счётчикик параметров и заголовков

    def last_report(self):
        """
        Признак последнего отчёта в списке

        :return True, если выведен последний отчёт из списка
        :rtype: bool
        """
        return self._last_report                            # возвращаем флаг последнего отчёта

    def add_report(self, filename):
        """
        Добавление отчёта по имени XML-описания

        :param filename: имя файла
        :type filename str
        """
        self._report_num += 1                               # продвигаем текущий отчёт
        try:                                                # пробуем
            self._report_xml = open(filename).read()        # открыть на чтение
        except IOError:                                     # не удалось
            print("IO/err: %s not found" % filename)        # обработка ошибки
            exit(1)                                         # и выход
        parm_cnt = 0                                        # считаем
        while self._report_xml.find(                        # количество
                        "$_parm%d_" % parm_cnt) >= 0:       # параметров
            parm_cnt += 1                                   # отчёта
        title_cnt = 0                                       # считаем
        while self._report_xml.find(                        # количество
                        "$_title%d_" % title_cnt) >= 0:     # заголовков
            title_cnt += 1                                  # отчёта
        for i in reversed(range(parm_cnt)):                 # заменяем
            self._report_xml = self._report_xml.replace(    # счётчики
                "$_parm%d_" % i,                            # параметров
                "$_parm%d_" % (self.parm_cnt + i)           # на нужные
            )                                               # значения
        self.parm_cnt += parm_cnt                           # продвигаем счётчик
        for i in reversed(range(title_cnt)):                # заменяем
            self._report_xml = self._report_xml.replace(    # счётчики
                "$_title%d_" % i,                           # заголовков
                "$_title%d_" % (self.title_cnt + i)         # на нужные
            )                                               # значения
        self.title_cnt += title_cnt                         # продвигаем счётчик
        self._file.write(self._report_xml)                  # пишем в файл

    def add_cycle(self):
        """
        Добавление следующего отчёта в цикле
        """
        if self.last_report():                              # предыдущий отчёт был последним
            self._report_type = 0                           # в списке, зацикливаем
            self._last_report = False                       # и начинаем вывод сначала
        self.report = self._reports[self._report_type]      # выбор и добавление
        self.add_report(self.report)                        # отчёта
        if self._report_type == len(self._reports) - 1:     # если выведен последний
            self._last_report = True                        # отчёт, взводим флаг
        else:                                               # иначе,
            self._report_type += 1                          # продвигаем тип

    def add_last(self):
        """
        Дублирование последнего выведенного отчёта
        """
        self.add_report(self.report)                        # дублировать последний

    def report_close(self):
        """
        Закрытие книги отчётов
        """
        self._file.write("</book>\n")                       # закрываем
        self._file.close()                                  # книгу


"""

Генерация отчётов на основании XML-описания и вывод их в .xls-файл
(Абстрактный класс)

"""


class BaseXLSReport(BaseXML):
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
            host, port, database, user, password, xml, [sql, title]
        :param param: параметры командной строки
        :type param: dict
        :raise psycopg2.Error ошибка соединения с БД
        :raise KeyError список параметров не содержит нужного параметра

        """
        self._param = param                                 # параметры класса
        self._parameters = {}                               # параметры отчёта
        self._set_parameters()                              # установить параметры, заменяемые из командной строки
        self._rows = None                                   # количество строк в отчёте
        self._styles = {}                                   # словарь предопределённых стилей
        self._rows_max = 0                                  # максимальное количество строк в запросе отчёта
        self._wb = xlwt.Workbook()                          # открытие книги .xls
        self._ws = None                                     # текущая страница книги .xls
        self._step = 1                                      # шаг отображения строки текущего отчёта
        self._curr = 0                                      # текущая строка отчёта
        self._sheet = 0                                     # номер текущей страницы книги .xls
        self._max = -1                                      # максимальный номер строки относительно начала отчёта
        self._field = 0                                     # текущее поле SQL-запроса
        BaseXML.__init__(self, param)                       # вызвать конструктор родителя
        self._conn = param['cursor']                        # курсор базы данных

    """

    Вывод отчёта в .xls-файл

    """

    def to_file(self, filename):
        """
        Вывод отчёта в .xls-файл

        :param filename: имя выходного файла
        :type filename: str
        """
        self.run_xml()                                      # обработать XML-файл
        self._wb.save(filename)                             # сохранить книгу .xls

    """

    "Protected" методы

    """
    """

    Установка параметров, подставляемых из командной строки

    """

    @abc.abstractmethod
    def _set_parameters(self):
        """
        Установка параметров, подставляемых
        из командной строки
        """
        raise NotImplementedError("Method not implemented")

    """

    Получение стиля указанного тега

    """

    def _get_style(self, node):
        """
        Получение стиля указанного тега

        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        :return: стиль указанного тега
        :rtype: XFStyle
        """
        style_name = self._get_attr(node, "stylename")      # имя стиля
        try:                                                # пробуем
            style = self._styles[style_name]                # выбрать описание
        except KeyError:                                    # не получилось
            style = ""                                      # стиль будет по умолчанию
        style_append = self._get_attr(node, "style")        # добавка для текущего элемента
        form = self._get_attr(node, "format")               # вытащить форма
        style += " " + style_append                         # добавить добавку
        if style + form not in self._styles:                # если нет стиля,
            self._styles[style + form] = xlwt.easyxf(style, form)  # создать и сохранить
        return self._styles[style + form]                   # вернуть стиль

    """

    Замена специальных переменных в базовом XML

    """

    def _replace_param(self, xml):
        """
        Замена специальных переменных в базовом XML

        :param xml: исходный XML
        :type xml: str
        :return: XML после замены переменных
        :rtype: str
        """
        return self.__subst_special_vars(xml)               # подстановка значений из командной строки

    """

    "Private" методы

    """
    """

    Замена специальной переменной в XML (статический метод)

    """

    @staticmethod
    def __subst_special_var(xml, parm, name):
        """
        Замена специальной переменной в XML

        :param xml: XML-строка
        :type xml: str
        :param parm: параметр командной строки
        :type parm: str
        :param name: имя специальной переменной без номера
        :type name str
        :return: изменённая XML-строка после подстановки
        :rtype: str

        """
        return xml.replace('{{%s}}' % name, parm)

    """

    Замена специальных переменных XML параметрами командной строки

    """
    def __subst_special_vars(self, xml):
        """
        Замена специальных переменных XML параметрами командной строки

        :param xml: XML-строка
        :type xml: str
        :return: изменённая XML-строка
        :rtype: str
        """
        for parameter in self._parameters:                               # цикл
            xml = self.__subst_special_var(xml,                          # замены
                                           self._parameters[parameter],  # по параметрам
                                           parameter)                    # командной строки
        return xml                                                       # вернуть результат
