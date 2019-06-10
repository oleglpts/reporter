#!/usr/bin/python3

# Required Debian packages: build-essential unixodbc-bin unixodbc-dev libsqliteodbc and other drivers
# See: https://github.com/mkleehammer/pyodbc/wiki/

import json
import importlib
from config import translate as _, logger, cmd_args
from utils.helpers import error_handler, database_connect

########################################################################################################################
#                                                  Entry point                                                         #
########################################################################################################################

if __name__ == '__main__':
    logger.info(_('reporter started'))
    logger.info('%s \'%s\'' % (_('report name'), cmd_args.name))
    try:
        with open('%s%s.json' % (cmd_args.reports, cmd_args.name), 'r') as config_file:
            report_config = json.load(config_file)
        form = report_config.get('format', 'csv')
        connect = database_connect(report_config['connection'], logger)
        cursor = connect.cursor()
        with open('%s.%s' % (cmd_args.output, form), 'w') as f:
            for sql in report_config['sql']:

                # to csv.py
                if sql.startswith('SKIP'):
                    skip = [x.strip() for x in sql.split('=')]
                    f.write((int(skip[1]) if len(skip) > 1 else 1) * '\n')
                    continue

                parameters_list = {
                    parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters
                }
                for parameter in parameters_list:
                    sql = sql.replace('{%s}' % parameter, parameters_list[parameter])
                logger.info('SQL: "%s"' % sql)
                cursor.execute(sql)
                getattr(
                    importlib.import_module('formats.%s' % form), form)(
                    cursor.fetchall(), report_config, cursor.description, f)
        cursor.close()
        connect.close()
        logger.info('%s \'%s.%s\'' % (_('output file'), cmd_args.output, form))
        logger.info(_('reporter ended'))
    except Exception as e:
        error_handler(logger, e, '', True)
