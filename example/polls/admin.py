from django.contrib import admin

from django_admin_tabs import (
    AdminChangeListTab,
    AdminTab,
    TabbedModelAdmin,
)
from .models import Answer, Choice, Poll


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 0


class PollAdminStep(AdminTab, admin.ModelAdmin):
    admin_tab_name = "Poll"
    fields = ("question",)
    inlines = (ChoiceInline,)


@admin.register(Answer)
class AnswerAdmin(AdminChangeListTab, admin.ModelAdmin):
    admin_tab_name = "Answers"
    model = Answer
    fk_field = "choice__poll"
    parent_model = Poll
    date_hierarchy = "timestamp"
    list_display = (
        "timestamp",
        "choice",
    )
    list_filter = ("choice",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["choice"].queryset = self.parent_object.choice_set.all()
        return form


@admin.register(Poll)
class PollAdmin(TabbedModelAdmin, admin.ModelAdmin):
    """The admin class that will render the change form with steps.

    All configuration for changelist are still valid.
    """

    admin_tabs = [
        PollAdminStep,
        AnswerAdmin,
    ]
