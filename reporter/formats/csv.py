import os
from reporter.utils.helpers import database_connect
from reporter.config import logger, cmd_args, translate as _


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
    with open('%s.csv' % cmd_args.output, 'w') as f:
        for sql in report_config['sql']:
            if sql.startswith('SKIP'):
                data, skip, description = [], [x.strip() for x in sql.split('=')], ()
                for _x in range(int(skip[1]) if len(skip) > 1 else 1):
                    data.append(('',))
            else:
                parameters_list = {
                    parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters
                }
                for parameter in parameters_list:
                    sql = sql.replace('{{%s}}' % parameter, parameters_list[parameter])
                cursor.execute(sql)
                data, description = cursor.fetchall(), cursor.description
            description_string = ''
            for column_name in description:
                description_string += '%s%s' % (column_name[0], report_config.get('field_delimiter', ';'))
            if description_string:
                f.write(description_string[:-1])
                f.write('\n')
            for row in data:
                data_string = ''
                for column in row:
                    data_string += '%s%s' % (column, report_config.get('field_delimiter', ';'))
                f.write(data_string[:-1])
                f.write('\n')
    cursor.close()
    connect.close()
    return True
