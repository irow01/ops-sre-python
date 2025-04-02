from user import views
from rest_framework.routers import SimpleRouter

urlpatterns = [
]

router = SimpleRouter()
router.register('auth', views.AuthView, basename='auth')
router.register('info', views.InfoView, basename='info')
router.register('logout', views.LogoutView, basename='logout')
router.register('password', views.PasswordView, basename='password')
router.register('permission', views.PermissionView, basename='permission')
router.register('role', views.RoleView, basename='role')
router.register('ad', views.ADView, basename='ad')
urlpatterns.extend(router.urls)
