from django.contrib import admin

from .models import Topic # モデルをインポート

# Register your models here.

admin.site.register(Topic) # 管理サイトでTopicモデルを操作可能にする