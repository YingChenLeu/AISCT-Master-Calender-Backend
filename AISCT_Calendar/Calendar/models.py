from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=254, unique=True)
    grade = models.IntegerField()


    def __str__(self):
        return self.username
class Event(models.Model):
    title=models.CharField(max_length=200)
    location=models.CharField(max_length=50)
    description=models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    def __str__(self):
        return self.title

class Assignment(models.Model):
    title=models.CharField(max=200)

class Day(models.Model):
    a_day = models.BooleanField(True)
    half_day = models.BooleanField(True)
    off_day = models.BooleanField(True)
    def __str__(self):
        return self.a_day
