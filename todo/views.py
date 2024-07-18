from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.timezone import make_aware, is_naive
from django.utils.dateparse import parse_datetime
from todo.models import Task


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
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")

    context = {
        'task': task,
    }
    return render(request, 'todo/detail.html', context)


# def reopen(request, task_id):
#     try:
#         task = Task.objects.get(pk=task_id)
#     except Task.DoesNotExist:
#         raise Http404("Task dose not exist")
#     task.completed = False
#     task.save()
#     return redirect('index')


def open_and_close(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task dose not exist")
    if task.completed == False:
        task.completed = True
        task.save()
    else:
        task.completed = False
        task.save()

    return redirect(index)


def update(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task does not exist")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.due_at = make_aware(parse_datetime(request.POST['due_at']))
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
