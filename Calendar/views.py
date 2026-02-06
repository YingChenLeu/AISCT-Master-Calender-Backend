from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils.dateparse import parse_date
from .models import Event,Assignment,Day



# class Index(APIView):
#     def get():
        
#         return Response({"message":"Hello this is calendar index"})

@api_view(['GET'])
def Index(request):
    data = {"message":"Hello this is calendar index"} 
    return Response(data)

@api_view(['GET'])
def getEventsRange(request):
    start_date = request.query_params.get('start')
    end_date = request.query_params.get('end')

    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)

        days=Day.objects.filter(date__range=(start_date, end_date))
        for day in days:
            events = Event.objects.filter(day=day)
            assignments = Assignment.objects.filter(day=day)
    else:
        events = Event.objects.all()
        assignments=Assignment.objects.all()

    events_data = [{
        "name": event.title,
        "start_time": event.start_time,
        "end_time": event.start_time,
        "description": event.description,
        } for event in events]
    assignments_data =[{
        "name": assignment.title,
        "class_name": assignment.class_name,
        "description": assignment.description,
        "posted_date": assignment.posted_date,
        "due_date": assignment.due_date,
        "google_classroom_link": assignment.google_classroom_link
    } for assignment in assignments]
    return Response({
        "events": events_data,
        "assignments": assignments_data
    })

@api_view(['POST'])
def addEvent(request):
    title = request.data.get('name')
    location = request.data.get('location')
    description = request.data.get('description')
    start_time = request.data.get('start')
    end_time = request.data.get('end')

    if title:
        event = Event.objects.create(title=title, location=location, description=description, start_time=start_time, end_time=end_time)
        return Response({"message": "Event added successfully", "event_id": event.id}, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Event Title Required"}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
def addAssignment(request):
    pass #will add later