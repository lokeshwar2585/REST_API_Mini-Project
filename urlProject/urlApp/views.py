from .models import *
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponseNotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
import string


def addcode():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class CreateShortUrl(APIView):
    def post(self, request):
        long_url= request.data.get('url')
        code=request.data.get('code')
        valid=request.data.get('validity',30)
        if not long_url:
            return Response({'error': 'URL is needed'},status=status.HTTP_400_BAD_REQUEST)
        if code:
            if Url.objects.filter(short_code=code).exists():
                return Response({'error': 'Code already exists'},status=status.HTTP_400_BAD_REQUEST)
        else:
            while True:
                code =addcode()
                if not Url.objects.filter(short_code=code).exists():
                    break
        my_url = Url.objects.create(
            url=long_url,
            short_code=code,
            validity=valid)

        exp_time = my_url.create_time + timezone.timedelta(minutes=int(valid))
        return Response({
            'short_link':f'http://localhost:8000/r/{code}/',
            'expires_at':exp_time
        }, status=status.HTTP_201_CREATED)

class GetUrlStats(APIView):
    def get(self, request, code):
        my_url =get_object_or_404(Url,short_code=code)
        expire=my_url.create_time+timezone.timedelta(minutes=my_url.validity)
        details=Detail.objects.filter(short=my_url).values('click_time','referrer','location')
        return Response({
            'original_url':my_url.url,
            'created_at':my_url.create_time,
            'validity':my_url.validity,
            'expires_at':expire,
            'clicks':my_url.clicks,
            'details':list(details)})


def redirect_url(request, code):
    try:
        my_url = Url.objects.get(short_code=code)
    except Url.DoesNotExist:
        return HttpResponseNotFound('Short URL not found.')

    expiry_time = my_url.create_time + timezone.timedelta(minutes=my_url.validity)
    if timezone.now() > expiry_time:
        return HttpResponseNotFound('URL expired.')
    my_url.clicks+=1
    my_url.save()
    Detail.objects.create(
        short=my_url,
        referrer=request.META.get('HTTP_REFERER',''),
        location='Unknown')
    return redirect(my_url.url)
