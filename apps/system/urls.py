from system import processViews, PermissionViews, views
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('workflow/status', processViews.WorkflowStatusView, basename='processStatus')
router.register('workflow/action', processViews.WorkflowActionView, basename='processAction')
router.register('workflow/transition', processViews.WorkflowTransitionView, basename='processTransition')
router.register('group/info', processViews.GroupInfoView, basename='groupInfo')
router.register('roles', processViews.RolesView, basename='roles')
router.register('workflow', processViews.WorkflowView, basename='workflow')
router.register('group', processViews.GroupView, basename='group')
router.register('workType', processViews.WorkTypeView, basename='workType')
router.register('permission', PermissionViews.PermissionView, basename='permission')
router.register('permissionUser', PermissionViews.PermissionUserView, basename='permissionUser')
router.register('statusList', processViews.StatusListView, basename='statusList')
router.register('image', views.ImageItemsView, basename='image')
urlpatterns.extend(router.urls)
