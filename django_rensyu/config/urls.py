"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include # ← includeを追記すること！

urlpatterns = [
    path('admin/', admin.site.urls),# URLパス → http://127.0.0.1:8000/admin/ にアクセスしたとき、Djangoが用意した管理画面のURLを読み込む（管理アプリを利用）
    path('', include('rensyu_app.urls')),  # ''← 空のパス → つまり「ルートURL（http://127.0.0.1:8000/）」に対応 → rensyu_appアプリのURLを読み込む
]
