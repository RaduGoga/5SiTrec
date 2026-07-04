from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Materie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='materii')
    nume = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nume']
        unique_together = ('user', 'nume')

    def __str__(self):
        return self.nume

    def media(self):
        note = self.note.all()
        if not note:
            return None
        return round(sum(n.valoare for n in note) / len(note), 2)

    def note_recente(self):
        return self.note.order_by('-data')[:5]


class Nota(models.Model):
    materie = models.ForeignKey(Materie, on_delete=models.CASCADE, related_name='note')
    valoare = models.FloatField()
    descriere = models.CharField(max_length=200, blank=True)
    data = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.materie.nume}: {self.valoare}"


class Absenta(models.Model):
    TIP_CHOICES = [('motivata', 'Motivată'), ('nemotivata', 'Nemotivată')]
    materie = models.ForeignKey(Materie, on_delete=models.CASCADE, related_name='absente')
    tip = models.CharField(max_length=20, choices=TIP_CHOICES, default='nemotivata')
    data = models.DateField(default=timezone.now)
    motiv = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.materie.nume} – {self.data}"


class StudyCheckin(models.Model):
    ORE_CHOICES = [
        ('0', '0h'),
        ('0.5', '30min'),
        ('1', '1h'),
        ('1.5', '1.5h'),
        ('2', '2h'),
        ('2.5', '2.5h'),
        ('3', '3h+'),
    ]
    PRODUCTIVITATE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    INTELEGERE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    STRES_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    data = models.DateField(default=timezone.now)
    ore_studiu = models.CharField(max_length=5, choices=ORE_CHOICES, default='1')
    productivitate = models.IntegerField(choices=PRODUCTIVITATE_CHOICES, default=3)
    intelegere = models.IntegerField(choices=INTELEGERE_CHOICES, default=3)
    stres = models.IntegerField(choices=STRES_CHOICES, default=3)

    class Meta:
        ordering = ['-data']
        unique_together = ('user', 'data')

    def __str__(self):
        return f"Check-in {self.data}"

    def consistency_score(self):
        score = 0
        ore = float(self.ore_studiu)
        if ore >= 2:
            score += 40
        elif ore >= 1:
            score += 25
        elif ore >= 0.5:
            score += 10
        score += (self.productivitate / 5) * 30
        score += (self.intelegere / 5) * 20
        score += ((6 - self.stres) / 5) * 10
        return round(score)


class WeeklyReflection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reflectii')
    saptamana_start = models.DateField()
    ce_a_mers = models.TextField(blank=True)
    ce_a_fost_dificil = models.TextField(blank=True)
    obiectiv = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-saptamana_start']
        unique_together = ('user', 'saptamana_start')

    def __str__(self):
        return f"Reflecție {self.saptamana_start}"
