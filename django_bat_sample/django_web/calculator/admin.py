from django.contrib import admin

from .models import Topic, Entry

# Register your models here.

admin.site.register(Topic) # 管理サイトでTopicモデルを操作可能にする
admin.site.register(Entry) # 管理サイトでEntryモデルを操作可能にする