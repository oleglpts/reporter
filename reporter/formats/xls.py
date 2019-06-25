import os
from reporter.config import logger, cmd_args
from reporter.utils.xls_report import XLSReport
from reporter.utils.helpers import database_connect


def xls(report_config):
    """

    Output report in csv

    :param report_config: report configuration
    :type report_config: dict

    """

    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s xls-%s' % (_('working'), _('generator')))
    XLSReport({
        'cursor': cursor,
        'xml': '%s%s.xml' % (cmd_args.reports, cmd_args.name),
        'logger': logger,
        'parameters': {parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters}
    }).to_file('%s.xls' % cmd_args.output)
    cursor.close()
    connect.close()
