"""
URLs configured for our remote cryptographic services.
"""
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^pythia/', include('pythiaPrfService.urls')),
)
