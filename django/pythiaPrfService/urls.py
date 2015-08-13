"""
URLs for interacting with the Pythia PRF service.
"""

from django.conf.urls import include, url
import views

urlpatterns = [

    # PRF evaluation requests
    url(r'^eval$',     views.evalVpop),
    url(r'^eval-unb$', views.evalVprf),
    url(r'^eval-bls$', views.evalBls),

    # Client-side key rotation
    url(r'^updateToken$',     views.updateTokenVpop),
    url(r'^updateToken-unb$', views.updateTokenVprf),
    url(r'^updateToken-bls$', views.updateTokenBls),
 
    # Key deletion
    url(r'^delete$',     views.deleteVpop),
    url(r'^delete-unb$', views.deleteVprf),
    url(r'^delete-bls$', views.deleteBls),

]
