import importlib
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponse
from gateway.menus import get_menu, get_tabs
from django.core.handlers.wsgi import WSGIRequest
from django.core.exceptions import PermissionDenied
from gateway.configs.config import SOFTWARE_VERSION

########################################################################################################################
#                                               Base class for reports                                                 #
########################################################################################################################


class BaseReport:

    def __init__(self):
        """

        Constructor

        """
        self.name = self.path = self.description = self.perm = self.form = self.sql = self.template = None
        self.fields = []

# ----------------------------------------------------------------------------------------------------------------------

    def render(self, request, form_parms=None, **kwargs):
        """

        Report rendering

        :param request: request
        :type request: WSGIRequest
        :param form_parms: initial form parameters
        :type form_parms: dict
        :return: response
        :rtype: HttpResponse

        """

        current_client = kwargs.pop('current_client') if 'current_client' in kwargs else 0
        parameters = {
            'path': self.path,
            'version': SOFTWARE_VERSION,
            'description': self.description,
            'menu': get_menu(request, reverse("main")),
            'tabs': get_tabs(request, reverse("main"), 'Reports'),
            'prefix': reverse("main"),
            'form': self.form(form_parms, current_client=current_client).as_api_table() if form_parms else self.form(
                current_client=current_client).as_api_table(),
            'report': self.name
        }
        for key in kwargs:
            parameters[key] = kwargs[key]
        return render(request, self.template, parameters)

# ----------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_report(request):
        """

        Get report by request

        :param request: request
        :type request: WSGIRequest
        :return: report object
        :rtype: BaseReport

        """
        report_name = request.GET.get('name', None)
        if report_name is None:
            raise Http404('Report name must be specified')
        try:
            report = getattr(
                importlib.import_module('gateway.reports.' + report_name[0:1].lower() + report_name[1:] + '_report'),
                report_name[0:1].upper() + report_name[1:] + 'Report')()
            report.form = report.form[0]
        except ImportError:
            raise Http404('Report \'%s\' not found' % report_name)
        if not request.user.has_perm(report.perm):
            raise PermissionDenied('403 - Permission denied')
        return report
