import os
from db_report.utils.callback import callback
from db_report.utils.helpers import database_connect
from db_report.config import logger, cmd_args, translate as _

data, description = None, None


def csv(report_config):
    """

    Output report in csv

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """
    global data, description

    suppress = report_config.get('suppress', 0)
    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s csv-%s' % (_('working'), _('generator')))
    skips = 0
    with open('%s.csv' % cmd_args.output, 'w') as f:
        for i, sql in enumerate(report_config['sql']):
            if sql.startswith('SKIP'):
                data, skip, description = [], [x.strip() for x in sql.split('=')], ()
                for _x in range(int(skip[1]) if len(skip) > 1 else 1):
                    data.append(('',))
                skips += 1
            else:
                parameters_list = {}
                for parm in cmd_args.parameters:
                    p = parm.split('=')
                    if p[1].endswith(','):
                        p[1] = p[1][:-1]
                    parameters_list[p[0]] = p[1]
                if sql.startswith('[evaluate]'):
                    sql = sql.split('[evaluate]')[1].split('[/evaluate]')[0].strip()
                    try:
                        with open(sql.replace('~', os.path.expanduser('~'))) as request_file:
                            code = compile(request_file.read(), sql, 'exec')
                            exec(code, globals(), locals())
                    except FileNotFoundError:
                        logger.error('file \'%s\' not found' % sql)
                        raise RuntimeError('file \'%s\' not found' % sql)
                else:
                    for parameter in parameters_list:
                        sql = sql.replace('{{%s}}' % parameter, parameters_list[parameter])
                    cursor.execute(sql)
                    data, description = cursor.fetchall(), cursor.description
                title_found = False
                title = 'title%s' % (i - skips)
                for parm in cmd_args.parameters:
                    if parm.startswith(title):
                        title_found = True
                        heading = parm.split('=')[1]
                        if heading[-1] == ',':
                            heading = heading[:-1]
                        f.write(heading)
                if not title_found:
                    f.write(report_config['headings'][i-skips])
                f.write('\n\n')
            description_string = ''
            for column_name in description:
                description_string += '%s%s' % (column_name[0], report_config.get('field_delimiter', ';'))
            if description_string:
                f.write(description_string[:-1])
                f.write('\n')
            length_data = len(data)
            suppress_list = [None] * len(description)
            for j, row in enumerate(data):
                suppress_enable, data_string = True, ''
                for k, column in enumerate(row):
                    if not column or column == 'None':
                        column = ''
                    if suppress_list and column != suppress_list[k]:
                        suppress_list[k] = column
                        suppress_enable = False
                    elif k < suppress and suppress_enable:
                        column = ''
                    column = str(column).split('/////')[0].strip()
                    data_string += '%s%s' % (column, report_config.get('field_delimiter', ';'))
                f.write(data_string[:-1])
                f.write('\n')
                if not (j + 1) % int(cmd_args.frequency):
                    callback({'status': -1, 'progress_data': j + 1, 'message': 'In progress',
                              'length_data': length_data})
            if not sql.startswith('SKIP'):
                callback({'status': -1, 'progress_data': length_data, 'message': 'In progress',
                          'length_data': length_data})
    cursor.close()
    connect.close()
    return True
