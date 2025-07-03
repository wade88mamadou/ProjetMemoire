from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.

@api_view(['GET'])
def test_connexion(request):
    return Response({"message": "Connexion OK entre Django et React !"})
