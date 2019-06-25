import logging
import argparse
import builtins
from utils.helpers import set_config, activate_virtual_environment, set_localization, get_logger

########################################################################################################################
#                                                 Configuration                                                        #
########################################################################################################################

parser = argparse.ArgumentParser(prog='reporter')
parser.add_argument('-c', '--config', help='config file', default='config/config.json')
parser.add_argument('-o', '--output', help='output file', default='./test')
parser.add_argument('-r', '--reports', help='reports directory', default='config/reports/')
parser.add_argument('-p', '--parameters', nargs='*', help='report parameters list', default=[])
parser.add_argument('-n', '--name', help='report name', default='test_csv')
parser.add_argument('-k', '--token', help='unique token for frontend', default='')
parser.add_argument('-b', '--callback_url', help='callback url', default='http://localhost:8080')
parser.add_argument('-l', '--log_level', help='logging level: CRITICAL, ERROR, WARNING, INFO, DEBUG or NOTSET',
                    default='INFO')

cmd_args = parser.parse_args()
config_args = set_config(cmd_args.config)

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
logger = get_logger('reporter', config_args.get("log_format", "%(levelname)-10s|%(asctime)s|"
                                                              "%(process)d|%(thread)d| %(name)s --- "
                                                              "%(message)s (%(filename)s:%(lineno)d)"),
                    config_args.get('log_file', '/tmp/reporter.log'), log_level)
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
