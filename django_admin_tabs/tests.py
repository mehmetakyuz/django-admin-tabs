from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from example.polls.models import Choice, Poll, Answer


class DjangoAdminTabsTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            is_staff=True,
            is_superuser=True,
            username="admin",
            password="admin",
        )

        self.poll = Poll.objects.create(question="What's up?")
        self.choice = Choice.objects.create(
            poll=self.poll,
            text="The sky is!",
        )
        self.answer = Answer.objects.create(
            choice=self.choice,
        )
        self.client.login(username="admin", password="admin")

    def test_admin_view_redirect(self):
        url = reverse("admin:polls_poll_change", args=(self.poll.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertURLEqual(
            response["location"],
            reverse("admin:polls_poll_step", args=(self.poll.id, "poll")),
        )

    def test_admin_view_tab(self):
        url = reverse("admin:polls_poll_step", args=(self.poll.id, "poll"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "admin/django_admin_tabs/tab_change_form.html"
        )
        self.assertTemplateUsed(response, "admin/django_admin_tabs/tabs_menu.html")

    def test_admin_view_changelist(self):
        url = reverse("admin:polls_poll_step", args=(self.poll.id, "answers"))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/django_admin_tabs/tabs_menu.html")
        self.assertTemplateUsed(
            response, "admin/django_admin_tabs/tab_change_list.html"
        )

    def test_admin_view_changelist_change(self):
        url = reverse(
            "admin:polls_poll_tab_change",
            args=(self.poll.id, "answers", self.choice.id),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/django_admin_tabs/tabs_menu.html")
        self.assertTemplateUsed(
            response, "admin/django_admin_tabs/tab_change_list_change.html"
        )

    def test_admin_view_changelist_add(self):
        url = reverse(
            "admin:polls_poll_tab_add",
            args=(self.poll.id, "answers"),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/django_admin_tabs/tabs_menu.html")

    def test_step_doesnt_exist(self):
        response = self.client.get(
            reverse(
                "admin:polls_poll_tab_add",
                args=(self.poll.id, "error"),
            )
        )
        self.assertEqual(response.status_code, 404)
