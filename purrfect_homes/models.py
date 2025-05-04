from django.db import models

class Cat(models.Model):
    GENDER = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER)
    breed = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100)
    description = models.TextField()
    vaccinated = models.BooleanField(default=False)
    neutered = models.BooleanField(default=False)
    photo = models.ImageField()
    arrival_date = models.DateField()
    adopted = models.BooleanField(default=False)
    medical_notes = models.TextField(blank=True)

    def __str__(self):
        return self.name