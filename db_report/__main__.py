#!/usr/bin/python3

# Required Debian packages: build-essential unixodbc-bin unixodbc-dev libsqliteodbc and other drivers (odbc-postgresql)
# See: https://github.com/mkleehammer/pyodbc/wiki/
#
# -n test_xls -p artist="Symphony Orchestra", title=Albums

import sys
import json
import time
import importlib

########################################################################################################################
#                                                 Main function                                                        #
########################################################################################################################


def main():
    sys.path.append('../')
    sys.path.append('/app')
    from db_report.utils.callback import server
    from db_report.utils.helpers import error_handler
    from db_report.utils.callback import callback_terminate
    from db_report.config import translate as _, logger, cmd_args
    if cmd_args.callback_url == 'http://localhost:8080' and cmd_args.token:
        server.start()
        time.sleep(1)
    form = None
    logger.info('%s, %s: %s' % (_('reporter started'), _('logging level'), cmd_args.log_level))
    logger.info('%s \'%s\'' % (_('report name'), cmd_args.name))
    try:
        with open('%s%s.json' % (cmd_args.reports, cmd_args.name), 'r') as config_file:
            report_config = json.load(config_file)
        form = report_config.get('format', 'csv')
        if cmd_args.database:
            report_config['connection'] = cmd_args.database
        report_config['headings'] = [x[1] for x in sorted(
            [[int(parm.split('=')[0][5:]), parm.split('=')[1]] for parm in cmd_args.parameters if
             parm.split('=')[0].startswith('title')])]
        if not report_config['headings'] and cmd_args.headings:
            report_config['headings'] = cmd_args.headings
        if cmd_args.sql:
            report_config['sql'] = cmd_args.sql.split('|||')
        condition_code = getattr(importlib.import_module('db_report.formats.%s' % form), form)(report_config)
        file_path = '%s.%s' % (cmd_args.output, form)
        logger.info('%s \'%s\'' % (_('output file'), file_path))
        if condition_code:
            callback_terminate(0, {'result': file_path, 'message': 'Success'})
        else:
            callback_terminate(3, {'result': 'empty', 'message': 'Fatal error'})
    except FileNotFoundError:
        logger.error("%s \'%s\' %s" % (_('report'), cmd_args.name, _('does not exists')))
        callback_terminate(1, {'result': 'empty', 'message': 'Report \'%s\' does not exists' % cmd_args.name})
    except ImportError as e:
        logger.error("%s \'%s\' %s" % (_('format'), form, _('not implemented')))
        callback_terminate(2, {'result': 'empty', 'message': 'Format \'%s\' not implemented' % form})
    except Exception as e:
        error_handler(logger, e, '', False, True)
        callback_terminate(3, {'result': 'empty', 'message': 'Unexpected error: %s' % str(e)})


########################################################################################################################
#                                                  Entry point                                                         #
########################################################################################################################


if __name__ == '__main__':
    main()
