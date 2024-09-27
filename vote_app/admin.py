from django.contrib import admin
from .models import Option, Vote, VoteHistory
# Register your models here.
admin.site.register(Option)
admin.site.register(Vote)
admin.site.register(VoteHistory)
