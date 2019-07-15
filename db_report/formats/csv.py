import os
from db_report.utils.callback import callback
from db_report.utils.helpers import database_connect
from db_report.config import logger, cmd_args, translate as _


def csv(report_config):
    """

    Output report in csv

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """

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
                parameters_list = {
                    parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters
                }
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
            for i, row in enumerate(data):
                data_string = ''
                for column in row:
                    data_string += '%s%s' % (column, report_config.get('field_delimiter', ';'))
                f.write(data_string[:-1])
                f.write('\n')
                if not (i + 1) % int(cmd_args.frequency):
                    callback({'status': -1, 'progress_data': i + 1, 'message': 'In progress',
                              'length_data': length_data})
            if not sql.startswith('SKIP'):
                callback({'status': -1, 'progress_data': length_data, 'message': 'In progress',
                          'length_data': length_data})
    cursor.close()
    connect.close()
    return True
