from order import views
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('OPSWorkOrder', views.OPSWorkOrderView, basename='OPSWorkOrder')
router.register('OPSWorkOrderData', views.OPSWorkOrderDataView, basename='OPSWorkOrderData')
router.register('WorkOrderInfoInRedis', views.WorkOrderInfoInRedis, basename='WorkOrderInfoInRedis')
urlpatterns.extend(router.urls)
