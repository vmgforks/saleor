from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import pgettext_lazy

from ..views import staff_member_required
from .forms import GroupPermissionsForm


@staff_member_required
def group_list(request):
    groups = Group.objects.all()
    ctx = {'groups': groups}
    return TemplateResponse(request, 'dashboard/group/list.html', ctx)


@staff_member_required
def group_create(request):
    group = Group()
    form = GroupPermissionsForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(
            request,
            pgettext_lazy('Dashboard message',
                          'Created group'))
        return redirect('dashboard:group-list')
    ctx = {'group': group, 'form': form}
    return TemplateResponse(request, 'dashboard/group/detail.html', ctx)


@staff_member_required
def group_details(request, pk):
    group = Group.objects.get(pk=pk)
    form = GroupPermissionsForm(request.POST or None, instance=group)
    if form.is_valid():
        form.save()
        messages.success(
            request,
            pgettext_lazy('Dashboard message', 'Updated group %s') % group.name
        )
    ctx = {'group': group, 'form': form}
    return TemplateResponse(request, 'dashboard/group/detail.html', ctx)


@staff_member_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        messages.success(
            request,
            pgettext_lazy('Dashboard message', 'Deleted group %s') % group
        )
        return redirect('dashboard:group-list')
    return TemplateResponse(
        request, 'dashboard/group/modal_group_confirm_delete.html',
        {'group': group}
    )