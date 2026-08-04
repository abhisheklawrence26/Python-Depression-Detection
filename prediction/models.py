from django.db import models

class User(models.Model):
    fullname = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username
    
    from django.db import models


class FaceEmotionResult(models.Model):

    username = models.CharField(max_length=100)

    happy = models.FloatField()

    sad = models.FloatField()

    neutral = models.FloatField()

    dominant_emotion = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username
    
from django.db import models


# DailyLog should be here
class DailyLog(models.Model):
    mood = models.CharField(max_length=30)
    stress = models.IntegerField()
    energy = models.IntegerField()
    sleep = models.CharField(max_length=50)
    activities = models.TextField()
    journal = models.TextField()

    def __str__(self):
        return self.mood
    
class HospitalSearch(models.Model):

    SEARCH_TYPE = (
        ("gps", "Current Location"),
        ("manual", "Manual Location"),
    )

    location = models.CharField(max_length=200)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    search_type = models.CharField(
        max_length=20,
        choices=SEARCH_TYPE,
        default="gps"
    )

    created_at = models.DateTimeField(auto_now_add=True)



