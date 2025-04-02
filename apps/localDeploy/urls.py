from localDeploy import views, OutApiViews
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('LocalProject', views.LocalProjectView, basename='LocalProject')
router.register('LocalOrder', views.LocalOrderView, basename='LocalOrder')
router.register('LocalOrderData', views.LocalOrderDataView, basename='LocalOrderData')
# router.register('iSIOT', OutApiViews.LocalOrderInfoView, basename='LocalOrderData')
urlpatterns.extend(router.urls)
