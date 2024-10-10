# voting/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Vote(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    key = models.CharField(max_length=100, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_votes', blank=True, default=0)
    deadline = models.DateTimeField(null=True, blank=True)  # Batas waktu opsional
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_created')  # Tambahkan field ini

    def __str__(self):
        return self.title

    def total_votes(self):
        return sum(option.votes for option in self.options.all())

    def total_likes(self):
        return self.likes.count()

    def is_active(self):
        """Mengembalikan True jika vote masih aktif atau tidak ada batas waktu."""
        if self.deadline:
            return timezone.now() < self.deadline
        return True
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
