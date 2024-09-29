# voting/models.py
from django.db import models
from django.contrib.auth.models import User

class Vote(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    key = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_votes', blank=True, default=0)

    def __str__(self):
        return self.title

    def total_votes(self):
        return sum(option.votes for option in self.options.all())

    def total_likes(self):
        return self.likes.count()


class Option(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.option_text

class VoteHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} voted {self.option.option_text} on {self.vote.title}'
