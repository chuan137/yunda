from django.shortcuts import render
from django.http import HttpResponse
import commen_utils

# Create your views here.
def index(request):
    return HttpResponse("get_cid: "+commen_utils.get_seq_by_code('c_id'))