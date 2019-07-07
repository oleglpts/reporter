import os
from xls_report import XLSReport
from db_report.config import logger, cmd_args
from db_report.utils.helpers import database_connect


def xls(report_config):
    """

    Output report in csv

    :param report_config: report configuration
    :type report_config: dict
    :return: True if no error
    :rtype: bool

    """

    connect = database_connect(report_config['connection'].replace('~', os.getenv('HOME')), logger)
    cursor = connect.cursor()
    logger.info('%s xls-%s' % (_('working'), _('generator')))
    report = XLSReport({
        'cursor': cursor,
        'xml': '%s%s.xml' % (cmd_args.reports, cmd_args.name),
        'logger': logger,
        'callback_url': cmd_args.callback_url,
        'callback_token': cmd_args.token,
        'callback_frequency': cmd_args.frequency,
        'parameters': {parm.split('=')[0]: parm.split('=')[1].replace(',', '') for parm in cmd_args.parameters}
    })
    report.to_file('%s.xls' % cmd_args.output)
    cursor.close()
    connect.close()
    return not report.fatal_error
