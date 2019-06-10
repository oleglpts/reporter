import os
import logging
import argparse
import builtins
from db_report.utils.helpers import set_config, activate_virtual_environment, set_localization, get_logger

########################################################################################################################
#                                                 Configuration                                                        #
########################################################################################################################

parser = argparse.ArgumentParser(prog='db_report')
home = os.getenv("HOME")
parser.add_argument('-c', '--config', help='config file', default='~/.db_report/config.json')
parser.add_argument('-o', '--output', help='output file', default='~/.db_report/test')
parser.add_argument('-r', '--reports', help='reports directory', default='~/.db_report/reports/')
parser.add_argument('-p', '--parameters', nargs='*', help='report parameters list', default=[])
parser.add_argument('-n', '--name', help='report name', required=True)
parser.add_argument('-k', '--token', help='unique token for frontend', default='')
parser.add_argument('-b', '--callback_url', help='callback url', default='http://localhost:8080')
parser.add_argument('-d', '--database', help='database connection string')
parser.add_argument('-q', '--sql', help='sql statement')
parser.add_argument('-e', '--headings', help='headings', nargs='*', default=[])
parser.add_argument('-f', '--frequency', help='callback frequency', default=10)
parser.add_argument('-l', '--log_level', help='logging level: CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET',
                    default='INFO')

cmd_args = parser.parse_args()
cmd_args.reports = cmd_args.reports.replace('~', home)
cmd_args.output = cmd_args.output.replace('~', home)
config_args = set_config(cmd_args.config.replace('~', home))

########################################################################################################################
#                                                  Localization                                                        #
########################################################################################################################

set_localization(**config_args)
translate = _ = builtins.__dict__.get('_', lambda x: x)


########################################################################################################################
#                                                    Logging                                                           #
########################################################################################################################

try:
    log_level, level_error = logging._nameToLevel[cmd_args.log_level], False
except KeyError:
    level_error = True
    log_level = logging._nameToLevel['INFO']
logger = get_logger('db_report', config_args.get("log_format", "%(levelname)-10s|%(asctime)s|"
                                                               "%(process)d|%(thread)d| %(name)s --- "
                                                               "%(message)s (%(filename)s:%(lineno)d)"),
                    config_args.get('log_file', '~/.report/report.log').replace('~', home), log_level)
if level_error:
    logger.warning('%s \'%s\', %s \'INFO\' %s' % (_('incorrect logging level'), cmd_args.log_level, _('used'),
                                                  _('by default')))
    cmd_args.log_level = 'INFO'


########################################################################################################################
#                                               Virtual environment                                                    #
########################################################################################################################

if config_args.get('environment') != "":
    activate_virtual_environment(**config_args)
    logger.info('%s \'%s\'' % (_('activated virtual environment'), config_args.get('environment')))
