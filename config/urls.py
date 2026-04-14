from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.static import serve
from django.urls import re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from geo.api_views import AttractionViewSet, GeographicObjectViewSet, QuizViewSet, RegionViewSet


api_router = DefaultRouter()
api_router.register('regions', RegionViewSet, basename='api-region')
api_router.register('objects', GeographicObjectViewSet, basename='api-object')
api_router.register('attractions', AttractionViewSet, basename='api-attraction')
api_router.register('quizzes', QuizViewSet, basename='api-quiz')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include(api_router.urls)),
    path('', include('geo.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# На production (DEBUG=False) helper static() не добавляет media-маршруты,
# поэтому явно раздаём media через Django view.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'insecure': True}),
]
