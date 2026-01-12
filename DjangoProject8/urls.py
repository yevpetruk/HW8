from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Task Manager API",
        default_version='v1',
        description="API для управления задачами с аутентификацией JWT",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@taskmanager.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Swagger документация
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),

    # Наше API (JWT токены теперь внутри tasks.urls)
    path('api/', include('tasks.urls')),
]