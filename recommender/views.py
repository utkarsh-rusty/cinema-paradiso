from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def get_content_based_recommendations(request):
    movie_title = request.query_params.get('movie_title', '')
    top_n = int(request.query_params.get('top_n', 10))
    weight_factor = float(request.query_params.get('weight_factor', 0.5))
    
    try:
        recommendations = get_content_based_recommendations(movie_title, top_n, weight_factor)
        return Response({'recommendations': recommendations.to_dict(orient='records')})
    except ValueError as e:
        return Response({'error': str(e)}, status=400)