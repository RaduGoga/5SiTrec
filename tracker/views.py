from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
import json
from datetime import date, timedelta

from .models import Materie, Nota, Absenta, StudyCheckin, WeeklyReflection
from .forms import MaterieForm, NotaForm, AbsentaForm, StudyCheckinForm, WeeklyReflectionForm


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cont creat cu succes!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required
def dashboard(request):
    user = request.user
    materii = Materie.objects.filter(user=user).prefetch_related('note', 'absente')

    # Medii per materie
    materii_data = []
    for m in materii:
        media = m.media()
        absente_count = m.absente.count()
        materii_data.append({'materie': m, 'media': media, 'absente': absente_count})

    # Media generala
    medii = [d['media'] for d in materii_data if d['media'] is not None]
    media_generala = round(sum(medii) / len(medii), 2) if medii else None

    # Total absente
    total_absente = sum(d['absente'] for d in materii_data)
    total_nemotivate = Absenta.objects.filter(materie__user=user, tip='nemotivata').count()

    # Materia cu cea mai slaba medie
    materii_cu_medie = [d for d in materii_data if d['media'] is not None]
    materie_slaba = min(materii_cu_medie, key=lambda x: x['media']) if materii_cu_medie else None
    materie_buna = max(materii_cu_medie, key=lambda x: x['media']) if materii_cu_medie else None

    # Consistency score (ultimele 7 zile)
    azi = date.today()
    checkins_recente = StudyCheckin.objects.filter(
        user=user,
        data__gte=azi - timedelta(days=6)
    )
    consistency_score = None
    if checkins_recente.exists():
        scores = [c.consistency_score() for c in checkins_recente]
        consistency_score = round(sum(scores) / len(scores))

    # Check-in de azi
    checkin_azi = StudyCheckin.objects.filter(user=user, data=azi).first()

    # Ultimele 5 note
    note_recente = Nota.objects.filter(materie__user=user).order_by('-data', '-created_at')[:5]

    # Tips & Insights
    insights = generate_insights(user, materii_data, total_nemotivate, consistency_score)

    # Chart data – medii per materie
    chart_labels = [d['materie'].nume for d in materii_cu_medie]
    chart_data = [d['media'] for d in materii_cu_medie]

    # Chart checkins ultimele 14 zile
    checkins_14 = StudyCheckin.objects.filter(
        user=user,
        data__gte=azi - timedelta(days=13)
    ).order_by('data')
    checkin_labels = [(azi - timedelta(days=i)).strftime('%d/%m') for i in range(13, -1, -1)]
    checkin_scores = []
    checkin_map = {c.data.strftime('%d/%m'): c.consistency_score() for c in checkins_14}
    for label in checkin_labels:
        checkin_scores.append(checkin_map.get(label, None))

    context = {
        'media_generala': media_generala,
        'total_absente': total_absente,
        'total_nemotivate': total_nemotivate,
        'materie_slaba': materie_slaba,
        'materie_buna': materie_buna,
        'consistency_score': consistency_score,
        'checkin_azi': checkin_azi,
        'note_recente': note_recente,
        'insights': insights,
        'materii_data': materii_data,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'checkin_labels': json.dumps(checkin_labels),
        'checkin_scores': json.dumps(checkin_scores),
    }
    return render(request, 'tracker/dashboard.html', context)


def generate_insights(user, materii_data, total_nemotivate, consistency_score):
    insights = []
    materii_cu_medie = [d for d in materii_data if d['media'] is not None]

    if total_nemotivate >= 5:
        insights.append({'tip': 'warning', 'text': f'Ai {total_nemotivate} absențe nemotivate. Ia în considerare recuperarea materiei.'})

    if materii_cu_medie:
        materie_slaba = min(materii_cu_medie, key=lambda x: x['media'])
        if materie_slaba['media'] < 5:
            insights.append({'tip': 'danger', 'text': f'Media la {materie_slaba["materie"].nume} este sub 5. Prioritizează această materie.'})
        elif materie_slaba['media'] < 7:
            insights.append({'tip': 'warning', 'text': f'{materie_slaba["materie"].nume} necesită atenție. Media actuală: {materie_slaba["media"]}.'})

        if len(materii_cu_medie) >= 2:
            max_med = max(materii_cu_medie, key=lambda x: x['media'])['media']
            min_med = min(materii_cu_medie, key=lambda x: x['media'])['media']
            if max_med - min_med > 3:
                insights.append({'tip': 'info', 'text': 'Există diferențe mari între materii. Echilibrează timpul de studiu.'})

    if consistency_score is not None:
        if consistency_score >= 75:
            insights.append({'tip': 'success', 'text': f'Consistency score ridicat ({consistency_score}/100). Continuă ritmul!'})
        elif consistency_score < 40:
            insights.append({'tip': 'warning', 'text': 'Regularitatea studiului este scăzută. Încearcă sesiuni zilnice scurte.'})

    if not insights:
        insights.append({'tip': 'info', 'text': 'Adaugă note și check-in-uri pentru a primi recomandări personalizate.'})

    return insights


@login_required
def materii_list(request):
    materii = Materie.objects.filter(user=request.user).prefetch_related('note', 'absente')
    form = MaterieForm()
    if request.method == 'POST':
        form = MaterieForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            messages.success(request, f'Materia „{m.nume}" a fost adăugată.')
            return redirect('materii')
    context = {'materii': materii, 'form': form}
    return render(request, 'tracker/materii.html', context)


@login_required
def materie_delete(request, pk):
    materie = get_object_or_404(Materie, pk=pk, user=request.user)
    if request.method == 'POST':
        name = materie.nume
        materie.delete()
        messages.success(request, f'Materia „{name}" a fost ștearsă.')
    return redirect('materii')


@login_required
def note_list(request):
    materii = Materie.objects.filter(user=request.user)
    note = Nota.objects.filter(materie__user=request.user).order_by('-data')
    form = NotaForm(user=request.user)
    if request.method == 'POST':
        form = NotaForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nota a fost adăugată.')
            return redirect('note')
    context = {'note': note, 'form': form, 'materii': materii}
    return render(request, 'tracker/note.html', context)


@login_required
def nota_delete(request, pk):
    nota = get_object_or_404(Nota, pk=pk, materie__user=request.user)
    if request.method == 'POST':
        nota.delete()
        messages.success(request, 'Nota a fost ștearsă.')
    return redirect('note')


@login_required
def absente_list(request):
    absente = Absenta.objects.filter(materie__user=request.user).order_by('-data')
    form = AbsentaForm(user=request.user)
    total_motivate = absente.filter(tip='motivata').count()
    total_nemotivate = absente.filter(tip='nemotivata').count()
    if request.method == 'POST':
        form = AbsentaForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absența a fost înregistrată.')
            return redirect('absente')
    context = {
        'absente': absente,
        'form': form,
        'total_motivate': total_motivate,
        'total_nemotivate': total_nemotivate,
    }
    return render(request, 'tracker/absente.html', context)


@login_required
def absenta_delete(request, pk):
    absenta = get_object_or_404(Absenta, pk=pk, materie__user=request.user)
    if request.method == 'POST':
        absenta.delete()
        messages.success(request, 'Absența a fost ștearsă.')
    return redirect('absente')


@login_required
def checkin_view(request):
    azi = date.today()
    checkin_azi = StudyCheckin.objects.filter(user=request.user, data=azi).first()
    checkins = StudyCheckin.objects.filter(user=request.user).order_by('-data')[:14]

    form = StudyCheckinForm(instance=checkin_azi)
    if request.method == 'POST':
        form = StudyCheckinForm(request.POST, instance=checkin_azi)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.data = azi
            c.save()
            messages.success(request, 'Check-in salvat!')
            return redirect('checkin')

    context = {'form': form, 'checkin_azi': checkin_azi, 'checkins': checkins}
    return render(request, 'tracker/checkin.html', context)


@login_required
def reflectii_list(request):
    azi = date.today()
    # Start of current week (Monday)
    start_saptamana = azi - timedelta(days=azi.weekday())
    reflectie_curenta = WeeklyReflection.objects.filter(
        user=request.user, saptamana_start=start_saptamana
    ).first()
    reflectii = WeeklyReflection.objects.filter(user=request.user)
    form = WeeklyReflectionForm(instance=reflectie_curenta)
    if request.method == 'POST':
        form = WeeklyReflectionForm(request.POST, instance=reflectie_curenta)
        if form.is_valid():
            r = form.save(commit=False)
            r.user = request.user
            r.saptamana_start = start_saptamana
            r.save()
            messages.success(request, 'Reflecția a fost salvată.')
            return redirect('reflectii')
    context = {
        'form': form,
        'reflectii': reflectii,
        'reflectie_curenta': reflectie_curenta,
        'start_saptamana': start_saptamana,
    }
    return render(request, 'tracker/reflectii.html', context)
