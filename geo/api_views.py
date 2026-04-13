from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from .models import Attraction, GeographicObject, Quiz, Region
from .serializers import (
    AttractionSerializer,
    GeographicObjectSerializer,
    QuizSerializer,
    RegionSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='Список областей'),
    retrieve=extend_schema(summary='Детали области'),
    create=extend_schema(summary='Создать область'),
    update=extend_schema(summary='Обновить область'),
    partial_update=extend_schema(summary='Частично обновить область'),
    destroy=extend_schema(summary='Удалить область'),
)
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'administrative_center']
    ordering_fields = ['name', 'population', 'area']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary='Список географических объектов'),
    retrieve=extend_schema(summary='Детали географического объекта'),
    create=extend_schema(summary='Создать географический объект'),
    update=extend_schema(summary='Обновить географический объект'),
    partial_update=extend_schema(summary='Частично обновить географический объект'),
    destroy=extend_schema(summary='Удалить географический объект'),
)
class GeographicObjectViewSet(viewsets.ModelViewSet):
    queryset = GeographicObject.objects.select_related('region').all()
    serializer_class = GeographicObjectSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location', 'region__name']
    ordering_fields = ['name', 'object_type']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary='Список достопримечательностей'),
    retrieve=extend_schema(summary='Детали достопримечательности'),
    create=extend_schema(summary='Создать достопримечательность'),
    update=extend_schema(summary='Обновить достопримечательность'),
    partial_update=extend_schema(summary='Частично обновить достопримечательность'),
    destroy=extend_schema(summary='Удалить достопримечательность'),
)
class AttractionViewSet(viewsets.ModelViewSet):
    queryset = Attraction.objects.select_related('region').all()
    serializer_class = AttractionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'region__name']
    ordering_fields = ['name']
    ordering = ['name']


@extend_schema_view(
    list=extend_schema(summary='Список тестов'),
    retrieve=extend_schema(summary='Детали теста с вопросами и ответами'),
    create=extend_schema(summary='Создать тест'),
    update=extend_schema(summary='Обновить тест'),
    partial_update=extend_schema(summary='Частично обновить тест'),
    destroy=extend_schema(summary='Удалить тест'),
)
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.prefetch_related('questions__answers').all()
    serializer_class = QuizSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title']
    ordering = ['title']
