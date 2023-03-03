from django.db import models


class Poll(models.Model):
    question = models.CharField(max_length=200)

    def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.poll} {self.text}"


class Answer(models.Model):
    timestamp = models.DateTimeField(auto_now=True, auto_created=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"Answer: {self.choice}"
