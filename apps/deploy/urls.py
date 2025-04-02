from deploy import views
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('project', views.ProjectView, basename='project')
router.register('subProject', views.SubProjectView, basename='subProject')
router.register('workOrder', views.WorkOrderView, basename='workOrder')
router.register('WorkOrderData', views.WorkOrderDataView, basename='WorkOrderData')
router.register('jenkins', views.JenkinsView, basename='jenkins')
urlpatterns.extend(router.urls)
