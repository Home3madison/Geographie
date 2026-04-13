from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError

from .models import Answer, Attraction, GeographicObject, Question, Quiz, Region, UserProfile


class AnswerInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        correct_count = 0

        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            if form.cleaned_data.get('is_correct'):
                correct_count += 1

        if correct_count != 1:
            raise ValidationError('У каждого вопроса должен быть ровно один правильный ответ.')


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3
    formset = AnswerInlineFormSet


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz')
    list_filter = ('quiz',)
    search_fields = ('text',)
    inlines = [AnswerInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'questions_count')
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('questions')

    @admin.display(description='Количество вопросов')
    def questions_count(self, obj):
        return obj.questions.count()


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'administrative_center', 'area', 'population')
    list_filter = ('administrative_center',)
    search_fields = ('name', 'administrative_center')
    ordering = ('name',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'image'),
        }),
        ('Статистика', {
            'fields': ('administrative_center', 'area', 'population'),
        }),
    )


@admin.register(GeographicObject)
class GeographicObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'object_type', 'region', 'location')
    list_filter = ('object_type', 'region')
    search_fields = ('name', 'location')
    autocomplete_fields = ('region',)
    ordering = ('name',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'object_type', 'region'),
        }),
        ('Локация', {
            'fields': ('location', 'latitude', 'longitude', 'map_link'),
        }),
        ('Медиа', {
            'fields': ('image',),
        }),
    )


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)
    autocomplete_fields = ('region',)
    ordering = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    autocomplete_fields = ('user',)


admin.site.site_header = 'Geographie — панель администратора'
admin.site.site_title = 'Geographie Admin'
admin.site.index_title = 'Управление контентом и API'
