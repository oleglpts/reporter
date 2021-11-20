import os
import json as json_lib
from db_report.utils.helpers import database_connect
from db_report.config import logger, cmd_args, translate as _

columns, data = None, None


def json(report_config):
    """

    Output report on json-format

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """
    global columns, data
    data_list = []
    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s json-%s' % (_('working'), _('generator')))
    with open('%s.json' % cmd_args.output, 'w') as f:
        for sql in report_config['sql']:
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
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, (str(y) if y is not None else '' for y in rw))) for rw in cursor.fetchall()]
            data_list.append(data)
        f.write(json_lib.dumps(data_list, ensure_ascii=False, indent=4))
    return True
