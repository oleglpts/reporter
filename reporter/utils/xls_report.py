# _*_ coding: utf-8 _*_

import abc
import xlwt
import pyodbc
import logging
import builtins
from lxml import etree
from io import BytesIO
from xlwt.Style import XFStyle

_ = builtins.__dict__.get('_', lambda x: x)


class BaseXML(object):
    """

    xml-file processing

    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, param):
        """

        Constructor

        Required parameter 'xml': path to xml-file

        :param param: parameters
        :type param: dict
        :raise IOError file not found or inaccessible
        :raise etree.XMLSyntaxError syntax error in XML
        :raise KeyError parameter not found ('xml')

        """
        self._fatal_error = False
        self._param = param
        self._tags = {}
        self._set_tags()
        self._logger = param['logger'] if 'logger' in param else logging.getLogger()
        try:
            xml = None
            if 'xml' in param:
                xml = open(param['xml']).read()
            elif 'xml_string' in param:
                xml = param['xml_string']
            else:
                self._logger.critical(_('XML not defined - terminating'))
                self._fatal_error = True
            if not self._fatal_error:
                xml = self._replace_param(xml)
                xml = BytesIO(bytes(xml.encode()))
                self._tree = etree.parse(xml)
        except IOError:
            self._logger.critical(_('XML not found - terminating'))
            self._fatal_error = True
        except etree.XMLSyntaxError as e:
            self._logger.critical('%s: %s' % (_('XML error'), str(e)))
            self._fatal_error = True
        except KeyError as e:
            self._logger.critical('%s %s %s %s' % (_('key'), str(e), _('not found'), _('terminating')))
            self._fatal_error = True

    @property
    def fatal_error(self):
        """

        Fatal error

        :return: True if fatal error

        """
        return self._fatal_error

    def run_xml(self):
        """

        xml file processing

        """
        self.__get_node(self._tree.getroot())

    @abc.abstractmethod
    def _set_tags(self):
        """

        Setting tag processing methods

        """
        raise NotImplementedError("Not implemented")

    @abc.abstractmethod
    def _replace_param(self, xml):
        """
        Replacing special variables in base XML

        :param xml: source XML
        :type xml: str
        :return: XML after replacing
        :rtype: str
        """
        raise NotImplementedError("Not implemented")

    @staticmethod
    def _get_attr(node, attr, default=""):
        """
        Getting attribute value

        :param node: parse tree element containing the tag
        :type node: _Element
        :param attr: attribute name
        :type attr: str
        :param default: default value
        :type default: str
        :return: attribute value
        :rtype: str
        :raise ValueError with encoding error
        """
        result = default
        try:
            result = node.attrib[attr]
        except KeyError:
            result = default
        except ValueError as e:
            print("Value Error: %s - %s" % (attr, str(e)))
            exit(1)
        return result

    @staticmethod
    def _get_int(number):
        """
        Convert digital string to binary integer

        :param number: integer in string representation
        :return: integer in binary representation
        :raise ValueError with non-numeric parameter value
        :raise UnicodeEncode error with encoding error
        """
        try:
            return int(number)
        except UnicodeEncodeError:
            print("UnicodeEncodeError: %s" % number)
            exit(1)
        except ValueError as e:
            print("Value Error: %s" % str(e))
            exit(1)

    @staticmethod
    def _string_to_list(source_string, delimiter=','):
        """

        Parameters string to list

        :param source_string: source string
        :type source_string: str
        :param delimiter: delimiter
        :type delimiter: str
        :return: parameters list
        :rtype: list

        """
        suppress = [x.strip() for x in source_string.split(delimiter)]
        return suppress if suppress != [''] else []

    def __get_node(self, node):
        """

        Tag processing

        :param node: XML tag
        :type node: _Element
        """
        if node.tag in self._tags:
            func = self._tags[node.tag]
            func(node)
        for n in node:
            self.__get_node(n)


class BaseXLSReport(BaseXML):
    """

    Report generation in xls-format according to the xml description (abstract class)

    """
    def __init__(self, param):
        """

        Constructor

        Required parameters: cursor, xml, [sql, title]

        :param param: parameters
        :type param: dict
        :raise KeyError required parameter expected

        """
        self._param = param
        self._parameters = {}
        self._set_parameters()
        self._rows = None
        self._styles = {}
        self._rows_max = 0
        self._wb = xlwt.Workbook()
        self._ws = None
        self._step = 1
        self._curr = 0
        self._sheet = 0
        self._max = -1
        self._field = 0
        BaseXML.__init__(self, param)
        self._conn = param['cursor']

    def to_file(self, filename):
        """

        Save report to .xls-file

        :param filename: output file name
        :type filename: str
        """
        if not self._fatal_error:
            self.run_xml()
            self._wb.save(filename)

    @abc.abstractmethod
    def _set_parameters(self):
        """

        Set parameters

        """
        raise NotImplementedError("Method not implemented")

    def _get_style(self, node, append=''):
        """
        Getting the style of the specified tag

        :param node: parse tree element containing the tag
        :type node: _Element
        :return: style of the specified tag
        :rtype: XFStyle
        """
        style_name = self._get_attr(node, "stylename")
        try:
            style = self._styles[style_name]
        except KeyError:
            style = ""
        style_append = self._get_attr(node, "style")
        form = self._get_attr(node, "format")
        style += " " + style_append + append
        if style + form not in self._styles:
            self._styles[style + form] = xlwt.easyxf(style, form)
        return self._styles[style + form]

    def _replace_param(self, xml):
        """

        Replacing special variables in base XML

        :param xml: source XML
        :type xml: str
        :return: XML after replacing
        :rtype: str
        """
        return self.__subst_special_vars(xml)

    @staticmethod
    def __subst_special_var(xml, parm, name):
        """
        Replacing special variable in XML

        :param xml: XML
        :type xml: str
        :param parm: parameter name
        :type parm: str
        :param name: special variable name
        :type name str
        :return: XML after substitution
        :rtype: str

        """
        return xml.replace('{{%s}}' % name, parm)

    def __subst_special_vars(self, xml):
        """
        Replacing special variables in XML

        :param xml: XML
        :type xml: str
        :return: XML after substitutions
        :rtype: str
        """
        for parameter in self._parameters:
            xml = self.__subst_special_var(xml,
                                           self._parameters[parameter],
                                           parameter)
        return xml


class XLSReport(BaseXLSReport):
    """

    Report generation in xls-format according to the xml description

    """
    def __init__(self, param):
        """
        Constructor

        Required parameters: cursor, xml, sql, title

        :param param: parameters
        :type param: dict

        """
        BaseXLSReport.__init__(self, param)

    def _set_parameters(self):
        """

        Set parameters

        """
        self._parameters = self._param['parameters']

    def _set_tags(self):
        """

        Setting tag processing methods

        """
        self._tags = {
            "report": self.get_report,
            "name": self.get_name,
            "literal": self.get_literal,
            "groupliteral": self.get_groupliteral,
            "sql": self.get_sql,
            "request": self.get_request,
            "group": self.get_group,
            "field": self.get_field,
            "formula": self.get_formula,
            "styledef": self.get_styledef
        }

    def get_report(self, node):
        """

        Tag <report> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        self._ws = None
        self._step = 1
        self._curr = 0
        self._max = -1
        self._field = 0
        self._rows_max = 0

    def get_styledef(self, node):
        """
        Tag <styledef> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        self._styles[self._get_attr(node, "name", "Normal")]\
            = node.text

    def get_literal(self, node):
        """
        Tag <literal> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        row = self._get_int(self._get_attr(node, "row"))
        col = self._get_int(self._get_attr(node, "col"))
        self._ws.write(row + self._curr, col, node.text,
                       self._get_style(node))

    def get_name(self, node):
        """
        Tag <name> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        sheet_name = node.text if node.text is not None \
            else "Sheet%d" % self._sheet
        self._sheet += 1
        self._ws = self._wb.add_sheet(sheet_name)

    def get_sql(self, node):
        """
        Tag <sql> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        if self._get_attr(node, "cycle", "no") == "no":
            self._curr = self._max+1
        self._field = 0
        self._rows = [(0,)]

    def get_request(self, node):
        """
        Tag <request> processing

        :param node: parse tree element containing the tag
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

    def get_group(self, node):
        """

        Tag <group> processing

        :param node: parse tree element containing the tag
        :type node: _Element

        """
        self._step = self._get_int(
            self._get_attr(node, "step", "1"))

    def get_field(self, node):
        """

        Tag <field> processing

        :param node: parse tree element containing the tag
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

    def get_formula(self, node):
        """

        Tag <formula> processing

        :param node: parse tree element containing the tag
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

    def get_groupliteral(self, node):
        """

        Tag <groupliteral> processing

        :param node: parse tree element containing the tag
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
