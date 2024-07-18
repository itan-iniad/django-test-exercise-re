from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware, is_naive
from django.utils.dateparse import parse_datetime
from todo.models import Task
import datetime


# Create your views here.
def index(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        overview = request.POST.get('overview')
        due_at_str = request.POST.get('due_at')

        if due_at_str:
            due_at = parse_datetime(due_at_str)
            if due_at is not None and is_naive(due_at):
                due_at = make_aware(due_at)
        else:
            due_at = None

        task = Task(title=title, overview=overview, due_at=due_at)
        task.save()

    if request.GET.get('order') == 'due':
        tasks = Task.objects.order_by('due_at')
    else:
        tasks = Task.objects.order_by('-posted_at')

    context = {
        'tasks': tasks
    }
    return render(request, 'todo/index.html', context)


def detail(request, task_id):
    dt_now = datetime.datetime.now()
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    
    if task.due_at is not None:
        year_days = (task.due_at.year - dt_now.year) * 365
        month_days = (task.due_at.month - dt_now.month) * 30
        day_days = task.due_at.day - dt_now.day
        days = year_days + month_days + day_days
    else:
        days = None  # または適切なデフォルト値

    context = {
        'task': task,
        'days': days
    }
    return render(request, 'todo/detail.html', context)


def open_and_close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task dose not exist")
    task.completed = not task.completed
    task.save()
    return redirect(index)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        due_at_str = request.POST.get('due_at')
        
        if due_at_str:
            due_at = parse_datetime(due_at_str)
            if due_at is not None and is_naive(due_at):
                due_at = make_aware(due_at)
        else:
            due_at = None

        task.due_at = due_at
        task.save()
        return redirect(detail, task_id)
    context = {
        'task': task
    }
    return render(request, "todo/edit.html", context)


def delete(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    task.delete()
    return redirect(index)
