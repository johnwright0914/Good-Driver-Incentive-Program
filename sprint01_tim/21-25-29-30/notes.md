## 21-25-29-30 Learning Django / webapp / Database technology

Learning Resource: [Django Documentation](https://docs.djangoproject.com/en/4.1/)
Covers 21, 25, 29, 30

Commands:

`pip install django`
`django-admin startproject tsite` This creates a new server in "tsite"
`python manage.py runserver` This Starts the server
`python manage.py runserver 8080`
`python manage.py runserver 0.0.0.0:8080`
`python manage.py startapp polls` Creates "polls/" for a poll app
`nvim polls/views.py` +=
```python 
from django.http import HttpResponse

def index(request):
	return HttpRespoinse("Hello, World!")
```
`nvim polls/urls.py` += 
```python 
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```
`nvim tsite/urls.py` +=
```python 
from django.urls import include, path

urlpatterns = [
	path('polls/', include('polls.urls')),
	path('admin/', admin.site.urls),
]
```
`python manage.py runserver`
`nvim polls/models.py` +=
```python 
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
```
`nvim tsite/settings.py` +=
```python 
INSTALLED_APPS = [
	'polls.apps.PollsConfig',
]
```
`python manage.py makemigrations polls`
`python manage.py sqlmigrate polls 0001`
`python manage.py migrate`
`python manage.py shell` >>>
```python 
from polls.models import Choice, question
Question.objects.all()
from django.utils import timezone
q = Question(question_text="What's new?", pub_date=timezone.now())
q.save()
q.id 
q.question_text
q.pub_date
q.question_text = "What's up?"
q.save()
Question.objects.all()
```
`nvim polls/models.py` +=
```python 
class Question(models.Model):
    # ...
    def __str__(self):
        return self.question_text
	
	def was_published_recently(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    # ...
    def __str__(self):
        return self.choice_text
```
`python manage.py shell` >>>
```python 
from polls.models import Choice, question_text
Question.objects.all()
Question.objects.filter(id=1)
Question.objects.filter(question_text__startswith='What')
from django.utils import timezone
current_year = timezone.now().year 
Question.objects.get(pub_date__year=current_year)
Question.objects.get(pk=1)
q = Question.objects.get(pk=1)
q.was_published_recently()
q = Question.objects.get(pk=1)
q.choice_set.all()
q.choice_set.create(choice_text='Not much', votes=0)
c = q.choice_set.create(choice_text='Just hacking again', votes=0)
c.question 
q.choice_set.all()
q.choice_set.count()
Choice.objects.filter(question__pub_date__year=current_year)
c = q.choice_set.filter(choice_text__startswith='Just hacking')
c.delete()
```
`python manage.py createsuperuser`
`nvim polls/admin.py` += 
```python 
from django.contrib import admin 
from .models import Question

admin.site.register(Question)
```
