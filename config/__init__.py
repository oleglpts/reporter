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
parser.add_argument('-n', '--name', help='report name', default='test')

cmd_args = parser.parse_args()
config_args = set_config(cmd_args.config)

########################################################################################################################
#                                                    Logging                                                           #
########################################################################################################################

logger = get_logger('reporter', config_args.get("log_format", "%(levelname)-10s|%(asctime)s|"
                                                              "%(process)d|%(thread)d| %(name)s --- "
                                                              "%(message)s (%(filename)s:%(lineno)d)"),
                    config_args.get('log_file', '/tmp/reporter.log'), logging.INFO)

########################################################################################################################
#                                                  Localization                                                        #
########################################################################################################################

set_localization(**config_args)
translate = _ = builtins.__dict__.get('_', lambda x: x)

########################################################################################################################
#                                               Virtual environment                                                    #
########################################################################################################################

if config_args.get('environment') != "":
    activate_virtual_environment(**config_args)
    logger.info('%s \'%s\'' % (_('activated virtual environment'), config_args.get('environment')))
