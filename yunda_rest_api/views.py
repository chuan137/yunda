# -*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework import viewsets, permissions
from yunda_parcel import models as parcel_models
from yunda_rest_api.serializers import ParcelSerializer, CustomerSerializer
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.reverse import reverse
from rest_framework.pagination import PageNumberPagination
import yunda_web_app
import json
from rest_framework.exceptions import ParseError
from django.utils import six
from userena.models import UserProfile

# Create your views here.
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'parcels': reverse('parcels_list', request=request, format=format),
    })
    
class ParcelList(generics.ListAPIView):
    queryset = parcel_models.Parcel.objects.filter(payment_status='pr_pas_paid').exclude(is_synced=True)[:yunda_web_app.settings.REST_FRAMEWORK['PAGINATE_BY']]
    serializer_class = ParcelSerializer
    #parser_classes = (UnicodeJSONParser,)
    permission_classes = (permissions.IsAdminUser,)
    
class ParcelDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = parcel_models.Parcel.objects.all()
    serializer_class = ParcelSerializer
    
class CustomerList(generics.ListAPIView):
    queryset = UserProfile.objects.exclude(is_synced=True)[:yunda_web_app.settings.REST_FRAMEWORK['PAGINATE_BY']]
    serializer_class = CustomerSerializer
    #parser_classes = (UnicodeJSONParser,)
    permission_classes = (permissions.IsAdminUser,)

@api_view(('POST',))
def api_set_customers_as_synced(request):
    queryset=UserProfile.objects.filter(customer_number__in=request.data)
    queryset.update(is_synced=True)
    return HttpResponse()

@api_view(('POST',))
def api_set_parcels_as_synced(request):
    queryset=parcel_models.Parcel.objects.filter(yde_number__in=request.data)
    queryset.update(is_synced=True)
    return HttpResponse()

@api_view(('POST',))
def api_update_tracking_number(request):
    for tracking_number in request.data:
        try:
            parcel=parcel_models.Parcel.objects.get(yde_number=tracking_number['yde_number'])
            parcel.tracking_number=tracking_number['tracking_number']
            parcel.save()
        except:
            pass
        #parcel.update(tracking_number=tracking_number['tracking_number'])
    return HttpResponse()
    
    
