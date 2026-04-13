from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import RegisterForm, UserProfileForm
from .models import Attraction, GeographicObject, Quiz, Region, UserProfile


def home(request):
    stats = {
        'regions_count': Region.objects.count(),
        'objects_count': GeographicObject.objects.count(),
        'attractions_count': Attraction.objects.count(),
        'quizzes_count': Quiz.objects.count(),
    }
    popular_regions = Region.objects.annotate(obj_count=Count('geographic_objects')).order_by('-obj_count')[:3]
    return render(request, 'geo/home.html', {'stats': stats, 'popular_regions': popular_regions})


def about(request):
    return render(request, 'geo/about.html')


def region_list(request):
    regions = Region.objects.all()
    return render(request, 'geo/region_list.html', {'regions': regions})


def region_detail(request, pk):
    region = get_object_or_404(Region, pk=pk)
    return render(request, 'geo/region_detail.html', {'region': region})


def object_list(request):
    query = request.GET.get('q', '').strip()
    objects = GeographicObject.objects.select_related('region').all()
    if query:
        objects = objects.filter(name__icontains=query)

    context = {
        'objects': objects,
        'query': query,
    }
    return render(request, 'geo/object_list.html', context)


def object_detail(request, pk):
    obj = get_object_or_404(GeographicObject.objects.select_related('region'), pk=pk)
    return render(request, 'geo/object_detail.html', {'object': obj})


def attraction_list(request):
    attractions = Attraction.objects.select_related('region').all()
    return render(request, 'geo/attraction_list.html', {'attractions': attractions})


def attraction_detail(request, pk):
    attraction = get_object_or_404(Attraction.objects.select_related('region'), pk=pk)
    return render(request, 'geo/attraction_detail.html', {'attraction': attraction})


def map_page(request):
    return render(request, 'geo/map.html')


def quiz_list(request):
    quizzes = Quiz.objects.annotate(total_questions=Count('questions')).all()
    return render(request, 'geo/quiz_list.html', {'quizzes': quizzes})


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('answers').all()

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if not answer_id:
                continue
            if question.answers.filter(id=answer_id, is_correct=True).exists():
                score += 1

        return redirect(f"{reverse('quiz_result', kwargs={'pk': quiz.pk})}?score={score}&total={total}")

    return render(request, 'geo/quiz_detail.html', {'quiz': quiz, 'questions': questions})


def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    score = int(request.GET.get('score', 0))
    total = int(request.GET.get('total', 0))
    percent = round((score / total) * 100, 1) if total else 0

    context = {
        'quiz': quiz,
        'score': score,
        'total': total,
        'percent': percent,
    }
    return render(request, 'geo/quiz_result.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно. Добро пожаловать!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из аккаунта.')
    return redirect('home')


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = UserProfileForm(instance=profile_obj)

    return render(request, 'geo/profile.html', {'form': form})
