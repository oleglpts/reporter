#!/usr/bin/python3

# Required Debian packages: build-essential unixodbc-bin unixodbc-dev libsqliteodbc and other drivers
# See: https://github.com/mkleehammer/pyodbc/wiki/
#
# -n test_xls -p artist="Symphony Orchestra", title=Albums

import sys
import json
import time
import importlib


########################################################################################################################
#                                                  Entry point                                                         #
########################################################################################################################


if __name__ == '__main__':
    sys.path.append('../')
    from reporter.utils.callback import server
    from reporter.utils.helpers import error_handler
    from reporter.utils.callback import callback_terminate
    from reporter.config import translate as _, logger, cmd_args
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
        getattr(importlib.import_module('reporter.formats.%s' % form), form)(report_config)
        file_path = '%s.%s' % (cmd_args.output, form)
        logger.info('%s \'%s\'' % (_('output file'), file_path))
        callback_terminate(0, {'result': file_path, 'message': 'Success'})
    except FileNotFoundError:
        logger.error("%s \'%s\' %s" % (_('report'), cmd_args.name, _('does not exists')))
        callback_terminate(1, {'result': 'empty', 'message': 'Report \'%s\' does not exists' % cmd_args.name})
    except ModuleNotFoundError as e:
        logger.error("%s \'%s\' %s" % (_('format'), form, _('not implemented')))
        callback_terminate(2, {'result': 'empty', 'message': 'Format \'%s\' not implemented' % form})
    except Exception as e:
        error_handler(logger, e, '', False, True)
        callback_terminate(3, {'result': 'empty', 'message': 'Unexpected error: %s' % str(e)})
