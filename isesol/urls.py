"""isesol URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, re_path
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^user/', include('apps.user.urls')),
    url(r'^system/', include('apps.system.urls')),
    url(r'^deploy/', include('apps.deploy.urls')),
    url(r'^localDeploy/', include('apps.localDeploy.urls')),
    url(r'^order/', include('apps.order.urls')),
    url(r'^host/', include('apps.host.urls')),
]
