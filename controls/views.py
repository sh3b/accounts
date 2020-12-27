import re
from itertools import chain, groupby

from accountancy.mixins import (ResponsivePaginationMixin,
                                SingleObjectAuditDetailViewMixin)
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.db.models import prefetch_related_objects
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)
from simple_history.utils import (bulk_create_with_history,
                                  bulk_update_with_history)
from users.mixins import LockDuringEditMixin

from controls.forms import (UI_PERMISSIONS, AdjustFinancialYearFormset,
                            FinancialYearForm,
                            FinancialYearInlineFormSetCreate, GroupForm,
                            PeriodForm, UserForm)
from controls.helpers import PermissionUI
from controls.models import FinancialYear, Period
from controls.widgets import CheckboxSelectMultipleWithDataAttr


class ControlsView(LoginRequiredMixin, TemplateView):
    template_name = "controls/controls.html"


class GroupsList(LoginRequiredMixin, ResponsivePaginationMixin, ListView):
    paginate_by = 25
    model = Group
    template_name = "controls/group_list.html"


class IndividualMixin:
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["edit"] = self.edit
        return context_data


class ReadPermissionsMixin:
    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        perms = self.get_perms()
        perm_ui = PermissionUI(perms)
        for perm in UI_PERMISSIONS.all():
            perm_ui.add_to_group(perm)
        perm_table_rows = perm_ui.create_table_rows()
        context_data["perm_table_rows"] = perm_table_rows
        return context_data


class GroupDetail(
        LoginRequiredMixin,
        SingleObjectAuditDetailViewMixin,
        ReadPermissionsMixin,
        IndividualMixin,
        DetailView):
    model = Group
    template_name = "controls/group_detail.html"
    edit = False

    def get_perms(self):
        return self.object.permissions.all()


class GroupUpdate(
        LoginRequiredMixin,
        LockDuringEditMixin,
        SingleObjectAuditDetailViewMixin,
        IndividualMixin,
        UpdateView):
    model = Group
    template_name = "controls/group_edit.html"
    success_url = reverse_lazy("controls:groups")
    form_class = GroupForm
    edit = True


class GroupCreate(LoginRequiredMixin, CreateView):
    model = Group
    template_name = "controls/group_edit.html"
    success_url = reverse_lazy("controls:groups")
    form_class = GroupForm


class UsersList(LoginRequiredMixin, ListView):
    paginate_by = 25
    model = User
    template_name = "controls/users_list.html"


"""

    The permissions tab in the UI for the user detail and user edit shows BOTH
    the permissions of the groups the user belongs to and the permissions for that particular user.

    In edit mode the user only has the option to change the latter.

"""


class UserDetail(
        LoginRequiredMixin,
        SingleObjectAuditDetailViewMixin,
        ReadPermissionsMixin,
        DetailView):
    model = User
    template_name = "controls/user_detail.html"
    edit = False

    def get_perms(self):
        user = self.object
        user_perms = user.user_permissions.all()
        prefetch_related_objects([user], "groups__permissions__content_type")
        group_perms = [group.permissions.all() for group in user.groups.all()]
        group_perms = list(chain(*group_perms))
        if user_perms and group_perms:
            return list(set(chain(user_perms, group_perms)))
        if user_perms:
            return user_perms
        if group_perms:
            return group_perms


class UserEdit(
        LoginRequiredMixin,
        LockDuringEditMixin,
        SingleObjectAuditDetailViewMixin,
        IndividualMixin,
        UpdateView):
    model = User
    form_class = UserForm
    template_name = "controls/user_edit.html"
    success_url = reverse_lazy("controls:users")
    edit = True

    # because 5 db hits are needed for POST
    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self):
        form = self.form_class(**self.get_form_kwargs())
        user = self.object
        prefetch_related_objects([user], "groups__permissions__content_type")
        group_perms = [group.permissions.all()
                       for group in user.groups.all()]  # does hit db again
        group_perms = list(chain(*group_perms))  # does not hit db again
        group_perms = {perm.pk: perm for perm in group_perms}
        self.group_perms = group_perms
        form.fields["user_permissions"].widget.group_perms = group_perms
        return form

    def form_valid(self, form):
        groups = form.cleaned_data.get("groups")
        user_permissions = form.cleaned_data.get("user_permissions")
        # because the group permissions are included in the form i.e. checkboxes are ticked for
        # permissions which belong to only groups and not users, we need to discount all such permissions
        user_permissions = [
            perm for perm in user_permissions if perm.pk not in self.group_perms]
        form.instance.user_permissions.clear()  # hit db
        form.instance.user_permissions.add(*user_permissions)  # hit db
        form.instance.groups.clear()  # hit db
        form.instance.groups.add(*groups)  # hit db
        form.save()  # hit db
        return super().form_valid(form)


class UserCreate(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = "controls/user_edit.html"
    success_url = reverse_lazy("controls:users")

    def get_form(self):
        self.form_class.declared_fields["user_permissions"].widget = CheckboxSelectMultipleWithDataAttr(
            attrs={
                "data-option-attrs": [
                    "codename",
                    "content_type__app_label",
                ],
            }
        )
        form = super().get_form()
        return form


class FinancialYearList(ListView):
    model = FinancialYear
    template_name = "controls/fy_list.html"


def convert_month_years_to_full_dates(post_data_copy):
    for k, v in post_data_copy.items():
        if re.search(r"month_end", k):
            if v:
                v = "01-" + v
                if re.search(r"01-\d{2}-\d{4}", v):
                    post_data_copy[k] = v
    return post_data_copy


class FinancialYearCreate(CreateView):
    model = FinancialYear
    template_name = 'controls/fy_create.html'
    form_class = FinancialYearForm
    success_url = reverse_lazy("controls:index")

    @transaction.atomic
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if self.request.POST:
            d = convert_month_years_to_full_dates(self.request.POST.copy())
            context_data["periods"] = FinancialYearInlineFormSetCreate(
                d, prefix="period")
        else:
            context_data["periods"] = FinancialYearInlineFormSetCreate(
                prefix="period")
        return context_data

    def form_valid(self, form):
        context_data = self.get_context_data()
        periods = context_data["periods"]
        if periods.is_valid():
            fy = form.save()
            self.object = fy
            periods.instance = fy
            periods.save(commit=False)
            period_instances = [p.instance for p in periods]
            period_instances.sort(key=lambda p: p.month_end)
            i = 1
            for period in period_instances:
                period.fy_and_period = f"{fy.financial_year}{str(i).rjust(2, '0')}"
                period.period = str(i).rjust(2, '0')
                i = i + 1
            bulk_create_with_history(
                [*period_instances],
                Period
            )
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(context_data)


class FinancialYearDetail(DetailView):
    model = FinancialYear
    template_name = "controls/fy_detail.html"
    context_object_name = "financial_year"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        periods = self.object.periods.all()
        context_data["periods"] = periods
        return context_data


class AdjustFinancialYear(UpdateView):
    model = Period
    template_name = "controls/fy_adjust.html"
    form_class = AdjustFinancialYearFormset
    success_url = reverse_lazy("controls:fy_list")
    prefix = "period"

    def get_object(self):
        # form is in fact a formset
        # so every period object can be edited
        return None

    def get_success_url(self):
        return self.success_url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        kwargs["queryset"] = Period.objects.all()
        return kwargs

    def form_invalid(self, formset):
        if any([form.non_field_errors() for form in formset]):
            formset.has_non_field_errors = True
        if formset.non_form_errors():
            formset.has_non_field_errors = True
        return super().form_invalid(formset)

    def form_valid(self, formset):
        formset.save(commit=False)
        instances = [form.instance for form in formset]
        fy_period_counts = {}
        for fy_id, periods in groupby(instances, key=lambda p: p.fy_id):
            fy_period_counts[fy_id] = len(list(periods))
        fys = FinancialYear.objects.all()
        for fy in fys:
            fy.number_of_periods = fy_period_counts[fy.pk]
        # no point auditing this
        FinancialYear.objects.bulk_update(fys, ["number_of_periods"])
        bulk_update_with_history(
            instances, Period, ["period", "fy_and_period", "fy"])
        return HttpResponseRedirect(self.get_success_url())
