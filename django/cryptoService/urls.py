"""
URLs configured for our remote cryptographic services.
"""
from django.conf.urls import  include, url
from django.contrib import admin

urlpatterns = [
    url(r'^pythia/', include('pythiaPrfService.urls')),
]
