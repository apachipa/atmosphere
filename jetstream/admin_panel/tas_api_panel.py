import copy
import logging

import collections
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.forms import TextInput, modelform_factory
from django.shortcuts import render

from jetstream import tas_api
from jetstream.exceptions import TASAPIException

TACC_USERNAME_FOR_XSEDE_USERNAME = 'TACC_USERNAME_FOR_XSEDE_USERNAME'
ACTIVE_ALLOCATIONS = 'ACTIVE_ALLOCATIONS'
PROJECTS_WITH_ACTIVE_ALLOCATION = 'PROJECTS_WITH_ACTIVE_ALLOCATION'
PROJECTS_FOR_USER = 'PROJECTS_FOR_USER'
USERS_FOR_PROJECT = 'USERS_FOR_PROJECT'

URL_TEMPLATES = {
    TACC_USERNAME_FOR_XSEDE_USERNAME: '/v1/users/xsede/{}',
    ACTIVE_ALLOCATIONS: '/v1/allocations/resource/{}',
    PROJECTS_WITH_ACTIVE_ALLOCATION: '/v1/projects/resource/{}',
    PROJECTS_FOR_USER: '/v1/projects/username/{}',
    USERS_FOR_PROJECT: '/v1/projects/name/{}/users'
}


class TACCUserForXSEDEUsername(models.Model):
    xsede_username = models.CharField('XSEDE Username', max_length=255)

    class Meta:
        app_label = 'jetstream'
        managed = False
        verbose_name = 'TACC User for XSEDE Username'

    @staticmethod
    def admin_panel_view(request, extra_context=None):
        return _get_tacc_user_for_xsede_username(request)


@staff_member_required
def _get_tacc_user_for_xsede_username(request):
    context = {}

    form_class = modelform_factory(TACCUserForXSEDEUsername,
                                   fields=['xsede_username'],
                                   widgets={'xsede_username': TextInput})

    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = form_class(request.POST)
        form.is_valid()
        xsede_username = form.cleaned_data['xsede_username']
        info, header, rows = _execute_tas_api_query(TACC_USERNAME_FOR_XSEDE_USERNAME, xsede_username)
        context['info'] = info
        context['header'] = header
        context['rows'] = rows
    else:
        form = form_class()

    context['form'] = form
    context['title'] = TACCUserForXSEDEUsername._meta.verbose_name

    return render(request, 'tas_api_query.html', context)


class ActiveAllocations(models.Model):
    resource = models.CharField('Resource', max_length=255, default='Jetstream')

    class Meta:
        app_label = 'jetstream'
        managed = False
        verbose_name = 'Active Allocations'

    @staticmethod
    def admin_panel_view(request, extra_context=None):
        return _get_active_allocations(request)


@staff_member_required
def _get_active_allocations(request):
    context = {}

    form_class = modelform_factory(ActiveAllocations,
                                   fields=['resource'],
                                   widgets={'resource': TextInput})

    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = form_class(request.POST)
        form.is_valid()
        resource = form.cleaned_data['resource']
        info, header, rows = _execute_tas_api_query(ACTIVE_ALLOCATIONS, resource)
        context['info'] = info
        context['header'] = header
        context['rows'] = rows
    else:
        form = form_class()

    context['form'] = form
    context['title'] = ActiveAllocations._meta.verbose_name

    return render(request, 'tas_api_query.html', context)


class ProjectsWithActiveAllocation(models.Model):
    resource = models.CharField('Resource', max_length=255, default='Jetstream')

    class Meta:
        app_label = 'jetstream'
        managed = False
        verbose_name = 'Projects with Active Allocation'

    @staticmethod
    def admin_panel_view(request, extra_context=None):
        return _get_projects_with_active_allocation(request)


@staff_member_required
def _get_projects_with_active_allocation(request):
    context = {}

    form_class = modelform_factory(ProjectsWithActiveAllocation,
                                   fields=['resource'],
                                   widgets={'resource': TextInput})

    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = form_class(request.POST)
        form.is_valid()
        resource = form.cleaned_data['resource']
        info, header, rows = _execute_tas_api_query(PROJECTS_WITH_ACTIVE_ALLOCATION, resource)
        context['info'] = info
        context['header'] = header
        context['rows'] = rows
    else:
        form = form_class()

    context['form'] = form
    context['title'] = ProjectsWithActiveAllocation._meta.verbose_name

    return render(request, 'tas_api_query.html', context)


class ProjectsForUser(models.Model):
    tacc_username = models.CharField('TACC Username', max_length=255, default='jlf599')

    class Meta:
        app_label = 'jetstream'
        managed = False
        verbose_name = 'Projects for User'

    @staticmethod
    def admin_panel_view(request, extra_context=None):
        return _get_projects_for_user(request)


@staff_member_required
def _get_projects_for_user(request):
    context = {}

    form_class = modelform_factory(ProjectsForUser,
                                   fields=['tacc_username'],
                                   widgets={'tacc_username': TextInput})

    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = form_class(request.POST)
        form.is_valid()
        tacc_username = form.cleaned_data['tacc_username']
        info, header, rows = _execute_tas_api_query(PROJECTS_FOR_USER, tacc_username)
        context['info'] = info
        context['header'] = header
        context['rows'] = rows
    else:
        form = form_class()

    context['form'] = form
    context['title'] = ProjectsForUser._meta.verbose_name

    return render(request, 'tas_api_query.html', context)


class UsersForProject(models.Model):
    project_charge_code = models.CharField('Project Charge Code', max_length=255, default='TG-TRA160003')

    class Meta:
        app_label = 'jetstream'
        managed = False
        verbose_name = 'Users for Project'

    @staticmethod
    def admin_panel_view(request, extra_context=None):
        return _get_users_for_project(request)


@staff_member_required
def _get_users_for_project(request):
    context = {}

    form_class = modelform_factory(UsersForProject,
                                   fields=['project_charge_code'],
                                   widgets={'project_charge_code': TextInput})

    if request.method == 'POST':
        request.POST = request.POST.copy()
        form = form_class(request.POST)
        form.is_valid()
        project_charge_code = form.cleaned_data['project_charge_code']
        info, header, rows = _execute_tas_api_query(USERS_FOR_PROJECT, project_charge_code)
        context['info'] = info
        context['header'] = header
        context['rows'] = rows
    else:
        form = form_class()

    context['form'] = form
    context['title'] = UsersForProject._meta.verbose_name

    return render(request, 'tas_api_query.html', context)


def _execute_tas_api_query(query_type, query=None):
    # return something like: 'Success', ['col1', 'col2'], [['row1_val1', 'row1_val2'], ['row2_val1', 'row2_val2']]
    tacc_api = settings.TACC_API_URL
    header = []
    rows = []
    url_template = URL_TEMPLATES[query_type]
    path = url_template.format(query)
    url = tacc_api + path

    try:
        response, data = tas_api.tacc_api_get(url)
        assert isinstance(data, dict)
        status = data.get('status', None)
        logging.debug('status: %s', status)
        message = data.get('message', None)
        logging.debug('message: %s', message)
        info = 'Response: {}, status: {}, message: {}'.format(response.__repr__(), status, message)
        result = data.get('result')
        logging.debug('result: %s', result)
        if result is None:
            # Probably an unknown user, project or resource. Don't do anything.
            logging.info('result is None: %s', info)
        elif isinstance(result, basestring):
            header = ['result']
            rows = [[result]]
        elif isinstance(result, collections.Sequence):
            result_headers = copy.copy(result[0].keys())
            hard_coded_headers = []
            trimmed_result_headers = list(set(result_headers) - set(hard_coded_headers))
            header = hard_coded_headers + trimmed_result_headers
            rows = [[row.get(key) for key in header] for row in result]
        else:
            raise ValueError('Unknown type for result: %s' % type(result))
    except TASAPIException as e:
        info = e
    return info, header, rows


__all__ = ['TACCUserForXSEDEUsername', 'ActiveAllocations', 'ProjectsWithActiveAllocation']
