import os
import json as json_lib
from db_report.utils.helpers import database_connect
from db_report.config import logger, cmd_args, translate as _


def json(report_config):
    """

    Output report on json-format

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """
    data_list = []
    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s json-%s' % (_('working'), _('generator')))
    with open('%s.json' % cmd_args.output, 'w') as f:
        for sql in report_config['sql']:
            parameters_list = {
                parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters
            }
            for parameter in parameters_list:
                sql = sql.replace('{{%s}}' % parameter, parameters_list[parameter])
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, (str(y) if y is not None else '' for y in rw))) for rw in cursor.fetchall()]
            data_list.append(data)
        f.write(json_lib.dumps(data_list, ensure_ascii=False, indent=4))
    return True
