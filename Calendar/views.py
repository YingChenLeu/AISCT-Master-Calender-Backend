from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view



# class Index(APIView):
#     def get():
        
#         return Response({"message":"Hello this is calendar index"})

@api_view(['GET'])
def Index(request):
    data = {"message":"Hello this is calendar index"} 
    return Response(data)

 
