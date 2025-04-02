from host import views
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('hostInfo', views.HostInfoView, basename='HostInfoView')
urlpatterns.extend(router.urls)
