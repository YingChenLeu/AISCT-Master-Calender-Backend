from rest_framework import serializers
from .models import Event
# from rest_framework.validators import UniqueValidator
# from django.contrib.auth.models import User

class EventSerializer(serializers.Serializer):
    class Meta:
        model = Event
        fields=['title','location','description','start_time','end_time']


    
    