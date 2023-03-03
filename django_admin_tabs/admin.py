from typing import List

from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.views.main import ChangeList
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.encoding import force_str
from django.utils.text import slugify


class AdminTab(admin.ModelAdmin):
    # Optionally override the model for this admin tab
    model = None

    # Optionally specify the name for this admin tab
    admin_tab_name = None

    change_form_template = "admin/django_admin_tabs/tab_change_form.html"
    change_list_template = "admin/django_admin_tabs/tab_change_list.html"

    def get_tab_name(self):
        return self.admin_tab_name or self.__class__.__name__

    def get_tab_slug(self):
        return force_str(slugify(self.get_tab_name()))

    def process_view(self, request, object_id, extra_context=None):
        return self.change_view(
            request=request,
            object_id=object_id,
            extra_context=extra_context,
        )

    def get_model_perms(self, request):
        """Removes the object from the admin index."""
        return {}


class AdminChangeListTab:
    admin_tab_name = None
    parent_model = None
    parent_object = None
    change_list_bulk_form = None

    # The field path to filter the queryset for the
    # changelist given the parent_object the changelist is nested under.
    # Can use full django ORM paths
    # For more advanced queryset filtering, override `get_queryset`
    fk_field = None

    ct_field = "content_type"
    ct_fk_field = "object_id"

    add_form_template = "admin/django_admin_tabs/tab_change_form.html"
    change_form_template = "admin/django_admin_tabs/tab_change_list_change.html"
    change_list_template = "admin/django_admin_tabs/tab_change_list.html"

    def get_tab_name(self):
        return self.admin_tab_name or self.__class__.__name__

    def get_tab_slug(self):
        return force_str(slugify(self.get_tab_name()))

    def get_queryset(self, request):
        from django.contrib.contenttypes.models import ContentType

        """Hook to override queryset for the nested changelist."""
        if self.fk_field:
            filters = {self.fk_field: self.parent_object}
        else:
            filters = {
                self.ct_field: ContentType.objects.get_for_model(self.parent_model),
                self.ct_fk_field: self.parent_object.id,
            }
        return super().get_queryset(request).filter(**filters)

    def save_model(self, request, obj, form, change):
        if self.fk_field:
            setattr(obj, self.fk_field, self.parent_object)
        else:
            setattr(obj, self.ct_fk_field.replace("_id", ""), self.parent_object)
        obj.save()

    def get_model_perms(self, request):
        """Removes the object from the admin index."""
        return {}

    def get_changelist(self, request, **kwargs):
        step = self.get_tab_slug()
        parent_object = self.parent_object
        admin_site = self.admin_site

        class AdminChangeList(ChangeList):
            def url_for_result(self, result):
                opts = parent_object._meta
                pk = getattr(result, self.pk_attname)
                return reverse(
                    f"{admin_site.name}:{opts.app_label}_{opts.model_name}_tab_change",
                    args=(parent_object.id, step, pk),
                )

        return AdminChangeList

    def get_changelist_form(self, request, **kwargs):
        return super().get_changelist_form(request, **kwargs)

    def process_view(self, request, object_id, extra_context=None):
        return self.changelist_view(
            request=request,
            object_id=object_id,
            extra_context=extra_context,
        )

    def changelist_view(self, request, object_id, extra_context=None):
        object = get_object_or_404(self.parent_model, id=object_id)
        opts = self.parent_model._meta
        model_name = self.parent_model._meta.model_name
        base_url_name = "%s_%s" % (self.parent_model._meta.app_label, model_name)
        model_actions_url_name = f"{base_url_name}_actions"
        self.tools_view_name = f"{self.admin_site.name}:{model_actions_url_name}"
        extra_context = extra_context or {}
        extra_context.update(
            {
                "has_change_permission": self.has_change_permission(request, None),
                "add_url": reverse(
                    f"{self.admin_site.name}:{opts.app_label}_{opts.model_name}_tab_add",
                    args=(object.id, self.get_tab_slug()),
                ),
            }
        )
        if self.change_list_bulk_form:
            changelist_action_form = self.change_list_bulk_form(
                parent_object=self.parent_object,
                data=request.POST if request.POST else None,
            )
            if (
                request.POST
                and "_submit_bulk" in request.POST
                and changelist_action_form.is_valid()
            ):
                created, updated = changelist_action_form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f"Bulk action performed. {created} created. {updated} updated.",
                )
            extra_context["changelist_action_form"] = changelist_action_form

        return super().changelist_view(request, extra_context=extra_context)

    def response_add(self, request, obj):
        """Determine the HttpResponse for the change_view stage."""
        opts = self.parent_model._meta
        if "_addanother" in request.POST:
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_tab_add"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug()),
                current_app=self.admin_site.name,
            )
        elif "_saveasnew" in request.POST:
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_tab_change"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug(), obj.id),
                current_app=self.admin_site.name,
            )
        else:
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_tab_change"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug(), obj.id),
                current_app=self.admin_site.name,
            )
        preserved_filters = self.get_preserved_filters(request)
        post_url = add_preserved_filters(
            {"preserved_filters": preserved_filters, "opts": opts}, post_url
        )
        return HttpResponseRedirect(post_url)

    def response_change(self, request, obj):
        """Determine the HttpResponse for the change_view stage."""
        response = super().response_change(request, obj)
        opts = self.parent_model._meta
        preserved_filters = self.get_preserved_filters(request)
        if "_addanother" in request.POST:
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_tab_add"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug()),
                current_app=self.admin_site.name,
            )
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
            return HttpResponseRedirect(post_url)
        elif "_continue" in request.POST:
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_tab_change"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug(), obj.id),
                current_app=self.admin_site.name,
            )
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
            return HttpResponseRedirect(post_url)
        return response

    def response_delete(self, request, obj_display, obj_id):
        opts = self.parent_model._meta
        if self.has_change_permission(request, None):
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_step"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug()),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_change(self, request, obj):
        opts = self.parent_model._meta
        if self.has_change_permission(request, None):
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_step"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug()),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)

    def response_post_save_add(self, request, obj):
        opts = self.parent_model._meta
        if self.has_change_permission(request, None):
            post_url = reverse(
                f"{self.admin_site.name}:%s_%s_step"
                % (opts.app_label, opts.model_name),
                args=(self.parent_object.id, self.get_tab_slug()),
                current_app=self.admin_site.name,
            )
            preserved_filters = self.get_preserved_filters(request)
            post_url = add_preserved_filters(
                {"preserved_filters": preserved_filters, "opts": opts}, post_url
            )
        else:
            post_url = reverse("admin:index", current_app=self.admin_site.name)
        return HttpResponseRedirect(post_url)


class TabbedModelAdmin:
    tabs_path = "tabs"
    admin_tabs = []

    def get_admin_tabs(self, request, object_id) -> List[AdminTab]:
        """Hook to dynamically return the enabled tabs."""
        return self.admin_tabs

    def get_initial_tab(self, request, object_id) -> AdminTab:
        """Hook to return the initial tab to load after adding a new object."""
        initial_step = self.admin_tabs[0]
        return initial_step(initial_step.model or self.model, self.admin_site)

    def get_admin_tab(self, request, object_id, step: str):
        object = get_object_or_404(self.model, id=object_id)
        instances = []
        for admin_class in self.get_admin_tabs(request, object):
            instance = admin_class(admin_class.model or self.model, self.admin_site)
            instance.parent_object = object
            instance.parent_model = self.model
            instances.append(instance)
        step_map = {step_admin.get_tab_slug(): step_admin for step_admin in instances}
        step_admin = step_map.get(step)
        if not step_admin:
            raise Http404(f"Tab '{step}' not found for {self}")
        return step_admin

    def change_view(self, request, object_id, form_url="", extra_context=None):
        step = self.get_initial_tab(request, object_id)
        return HttpResponseRedirect(
            reverse(
                f"{self.admin_site.name}:{self.model._meta.app_label}_{self.model._meta.model_name}_step",
                args=[object_id, step.get_tab_slug()],
            )
        )

    def get_context(self, request, instance, step):
        return dict(
            instance_meta_opts=instance._meta,
            admin_tabs=[
                step(step.model or self.model, self.admin_site)
                for step in self.get_admin_tabs(request, instance.id)
            ],
            current_tab=step,
            anchor=instance,
        )

    def response_add(self, request, obj, *args, **kwargs):
        return self.change_view(request, obj.id)

    def response_post_save_change(self, request, obj):
        return HttpResponseRedirect(request.path)

    def get_urls(self):
        base_urls = super().get_urls()
        prefix = f"{self.model._meta.app_label}_{self.model._meta.model_name}"
        wizard_urls = [
            path(
                f"<str:object_id>/{self.tabs_path}/<str:step>/<str:nested_object_id>/change/",
                self.admin_site.admin_view(self.nested_change_view),
                name=f"{prefix}_tab_change",
            ),
            path(
                f"<str:object_id>/{self.tabs_path}/<str:step>/add/",
                self.admin_site.admin_view(self.nested_add_view),
                name=f"{prefix}_tab_add",
            ),
            path(
                "<path:object_id>/{self.tabs_path}/<str:step>/<str:nested_object_id>/delete/",
                self.admin_site.admin_view(self.nested_delete_view),
                name=f"{prefix}_tab_delete",
            ),
            path(
                f"<str:object_id>/{self.tabs_path}/<str:step>/",
                self.admin_site.admin_view(self.tab_change_view),
                name=f"{prefix}_step",
            ),
        ]
        return wizard_urls + base_urls

    def tab_change_view(self, request, object_id, step):
        object = get_object_or_404(self.model, id=object_id)
        return self.get_admin_tab(request, object_id, step).process_view(
            request=request,
            object_id=object_id,
            extra_context=self.get_context(request, object, step),
        )

    def nested_change_view(self, request, object_id, step, nested_object_id=None):
        object = get_object_or_404(self.model, id=object_id)
        context = self.get_context(request, object, step)
        context["show_delete"] = False
        return self.get_admin_tab(request, object_id, step).change_view(
            request=request,
            object_id=nested_object_id,
            extra_context=context,
        )

    def nested_add_view(self, request, object_id, step):
        object = get_object_or_404(self.model, id=object_id)
        return self.get_admin_tab(request, object_id, step).add_view(
            request=request,
            extra_context=self.get_context(request, object, step),
        )

    def nested_delete_view(self, request, object_id, step, nested_object_id=None):
        object = get_object_or_404(self.model, id=object_id)
        return self.get_admin_tab(request, object_id, step).delete_view(
            request=request,
            nested_object_id=nested_object_id,
            extra_context=self.get_context(request, object, step),
        )
