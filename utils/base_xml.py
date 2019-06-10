# _*_ coding: utf-8 _*_

import abc
from lxml import etree
from io import BytesIO


class BaseXML(object):
    __metaclass__ = abc.ABCMeta

    """

    "Public" методы

    """
    """

    Конструктор

    """

    def __init__(self, param):
        """
        Конструктор

        Список параметров должен содержать 'xml': путь к файлу
        :param param: параметры класса
        :type param: dict
        :raise IOError нет файла .xml или он недоступен
        :raise etree.XMLSyntaxError синтаксическая ошибка в XML
        :raise KeyError нет нужного параметра ('xml')
        """
        self._param = param                                 # параметры класса
        self._tags = {}                                     # теги для обработки
        self._set_tags()                                    # установить обрабатываемые теги
        try:                                                # пробуем
            xml = None                                      # initialization
            if 'xml' in param:                              # задан файл XML
                xml = open(param['xml']).read()             # чтение XML-файла в строку
            elif 'xml_string' in param:                     # задана строка XML
                xml = param['xml_string']                   # принимаем её
            else:                                           # XML не задан
                print("Error: XML not defined")             # обработка ошибки
                exit(1)                                     # и аварийный выход
            xml = self._replace_param(xml)                  # замены строк в исходном XML
            xml = BytesIO(bytes(xml.encode()))              # файловый объект, готовый для обработки
            self._tree = etree.parse(xml)                   # разбор XML
        except IOError:                                     # ошибка ввода-вывода
            print("IO/err: XML-file not found")             # файл XML
            exit(1)                                         # не найден
        except etree.XMLSyntaxError as e:                   # ошибка разбора XML
            print("XML error: %s" % str(e))                 # синтаксическая
            exit(1)                                         # ошибка
        except KeyError as e:                               # список параметров
            print("Key Error: %s not found" % str(e))       # не содержит
            exit(1)                                         # нужного значения

    """

    Обработка XML-файла

    """

    def run_xml(self):
        """
        Обработка XML-файла
        """
        self.__get_node(self._tree.getroot())               # обработать XML-файл

    """

    "Protected" методы

    """
    """

    Установка методов обработки тегов

    """

    @abc.abstractmethod
    def _set_tags(self):
        """
        Установка методов обработки тегов
        """
        raise NotImplementedError("Not implemented")        # абстрактный метод

    """

    Замена специальных переменных в базовом XML

    """

    @abc.abstractmethod
    def _replace_param(self, xml):
        """
        Замена специальных переменных в базовом XML

        :param xml: исходный XML
        :type xml: str
        :return: XML после замены переменных
        :rtype: str
        """
        raise NotImplementedError("Not implemented")        # абстрактный метод

    """

    Получение значения атрибута (статический метод)

    """

    @staticmethod
    def _get_attr(node, attr, default=""):
        """
        Получение значения атрибута

        :param node: элемент дерева разбора, содержащий тег
        :type node: _Element
        :param attr:
        :type attr: str
        :param default:
        :type default: str
        :return: значение атрибута
        :rtype: str
        :raise ValueError при ошибке кодировки
        """
        result = default                                    # значение по умолчанию
        try:                                                # пробуем
            result = node.attrib[attr]                      # в лоб забрать значение
        except KeyError:                                    # нет атрибута
            result = default                                # значение по умолчанию
        except ValueError as e:                             # ошибка значения
            print("Value Error: %s - %s" % (attr, str(e)))  # вывести сообщение
            exit(1)                                         # выйти
        return result

    """

    Преобразование цифровой строки в двоичное целое

    """

    @staticmethod
    def _get_int(number):
        """
        Преобразование цифровой строки в двоичное целое

        :param number: целое число в строковом представлении
        :return: целое число в двоичном представлении
        :raise ValueError при нечисловом значении параметра
        :raise UnicodeEncode error при ошибке кодировки
        """
        try:                                                # пробуем
            return int(number)                              # преобразовать
        except UnicodeEncodeError:                          # ошибка
            print("UnicodeEncodeError: %s" % number)        # кодировки
            exit(1)                                         # выйти
        except ValueError as e:                             # ошибка:
            print("Value Error: %s" % str(e))               # нецифровое значение
            exit(1)                                         # выйти

    """

    "Private" методы

    """
    """

    Обработка тега

    """

    def __get_node(self, node):
        """
        Обработка тега

        :param node: тег XML
        :type node: _Element
        """
        if node.tag in self._tags:                          # если тег обрабатывается,
            func = self._tags[node.tag]                     # вытащить метод
            func(node)                                      # и вызвать его
        for n in node:                                      # следующий
            self.__get_node(n)                              # шаг рекурсии
