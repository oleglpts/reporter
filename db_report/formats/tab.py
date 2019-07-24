import os
import json
from db_report.utils.callback import callback
from db_report.utils.helpers import database_connect
from db_report.config import logger, cmd_args, translate as _


def tab(report_config):
    """

    Output report for jquery.dataTables

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """
    data_list, columns_list, suppress = [], [], report_config.get('suppress', 0)
    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s tab-%s' % (_('working'), _('generator')))
    with open('%s.tab' % cmd_args.output, 'w') as f:
        for sql in report_config['sql']:
            if sql.startswith('SKIP'):
                data, skip, description = [], [x.strip() for x in sql.split('=')], ()
                for _x in range(int(skip[1]) if len(skip) > 1 else 1):
                    data_list.append([])
            else:
                parameters_list = {
                    parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters
                }
                for parameter in parameters_list:
                    sql = sql.replace('{{%s}}' % parameter, parameters_list[parameter])
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, (str(y) for y in rw))) for rw in cursor.fetchall()]
                columns_list.append(columns)
                data_list.append(data)
        max_row_len = max([len(x) for x in columns_list])
        data_file = []
        if len(data_list):
            for i, columns in enumerate(columns_list):
                while data_list and not data_list[i]:
                    data_file.append(['' for _x in range(max_row_len)])
                    data_list.pop(i)
                if not data_list:
                    data_file = []
                suppress_list = [None] * max_row_len
                if len(columns_list) > 1:
                    row_data = ['<b><u>%s</u></b>' % report_config['headings'][i]]
                    while len(row_data) < max_row_len:
                        row_data.append('')
                    data_file.append(row_data)
                    row_data = []
                    for column in columns:
                        row_data.append('<b>%s</b>' % column)
                    while len(row_data) < max_row_len:
                        row_data.append('')
                    data_file.append(row_data)
                if not data_list:
                    break
                data_length = len(data_list[i])
                for j, row in enumerate(data_list[i]):
                    suppress_enable, row_data = True, []
                    for k, column in enumerate(columns_list[i]):
                        if not row[column] or row[column] == 'None':
                            row[column] = ''
                        if row[column] != suppress_list[k]:
                            suppress_list[k] = row[column]
                            suppress_enable = False
                        elif k < suppress and suppress_enable:
                            row[column] = ''
                        row_data.append(row[column].split('/////')[0].strip())
                    while len(row_data) < max_row_len:
                        row_data.append('')
                    data_file.append(row_data)
                    if i == len(columns_list) - 1 and not (j + 1) % int(cmd_args.frequency):
                        callback({'status': -1, 'progress_data': j + 1, 'message': 'In progress',
                                  'length_data': data_length})
                if i == len(columns_list) - 1:
                    callback({'status': -1, 'progress_data': data_length, 'message': 'In progress',
                              'length_data': data_length})
                if len(columns_list) > 1:
                    row_data = []
                    while len(row_data) < max_row_len:
                        row_data.append('')
                    data_file.append(row_data)
            if len(columns_list) > 1:
                data_file = data_file[:-1]
        f.write(json.dumps({"data": data_file}, indent=4))
        return True
