from django.db import models
from models import 

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=254, unique=True)
    grade = models.IntegerField()


    def __str__(self):
        return self.username



class Day(models.Model):
    a_day = models.BooleanField(True)
    half_day = models.BooleanField(True)
    off_day = models.BooleanField(True)
    date = models.DateField()
    def __str__(self):
        return self.date

class Assignment(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE())
    title=models.CharField(max_length=200)
    class_name=models.CharField(max_length=50)
    description=models.CharField(max_length=200)
    posted_date = models.DateTimeField()
    due_date = models.DateTimeField()
    google_classroom_link = models.URLField(max_length=200)
    def __str__(self):
        return self.title

class Event(models.Model):
    title=models.CharField(max_length=200)
    location=models.CharField(max_length=50)
    description=models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        return self.title

