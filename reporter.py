#!/usr/bin/python3

# Required Debian packages: build-essential unixodbc-bin unixodbc-dev libsqliteodbc and other drivers
# See: https://github.com/mkleehammer/pyodbc/wiki/
#
# -n test_xls -p artist="Symphony Orchestra", title=Albums


import json
import importlib
from utils.helpers import error_handler
from config import translate as _, logger, cmd_args

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
        getattr(importlib.import_module('formats.%s' % form), form)(report_config)
        logger.info('%s \'%s.%s\'' % (_('output file'), cmd_args.output, form))
        logger.info(_('reporter ended'))
    except Exception as e:
        error_handler(logger, e, '', True, True)
