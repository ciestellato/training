from django.shortcuts import render, redirect

from .models import Topic
from .forms import TopicForm, EntryForm

# Create your views here.
def index(request):
    """学習ノートのホームページ"""
    return render(request, 'learning_logs/index.html')

def topics(request):
    """すべてのトピックを表示する"""
    topics = Topic.objects.order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)

def topic(request, topic_id):
    """1つのトピックとそれについれのすべての記事を表示"""
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)

def new_topic(request):
    """新規トピックを追加する"""
    if request.method != 'POST':
        # データは送信されていないので空のフォームを生成する
        form = TopicForm()
    else:
        # POSTでデータが送信されたのでこれを処理する
        form = TopicForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topics')
    
    # 空または無効のフォームを表示する
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

def new_entry(request, topic_id):
    """特定のトピックに新規記事を追加する"""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # データは送信されていないので空のフォームを生成する
        form = EntryForm()
    else:
        # POSTデータが送信されたのでこれを処理する
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)
    
    # 空または無効のフォームを表示する
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)
