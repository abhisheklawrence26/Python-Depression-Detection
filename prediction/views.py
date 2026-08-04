# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect
from .models import User, DailyLog , HospitalSearch , FaceEmotionResult
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

import json
import base64
import cv2
import numpy as np
from deepface import DeepFace
import requests
import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import HospitalSearch


# ---------------- LOGIN ----------------

def login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            User.objects.get(email=email, password=password)
            return redirect("dashboard")

        except User.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid Email or Password"
            })

    return render(request, "login.html")


# ---------------- SIGNUP ----------------

def signup(request):

    if request.method == "POST":

        User.objects.create(
            fullname=request.POST.get("fullname"),
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            phone=request.POST.get("phone"),
            age=request.POST.get("age"),
            gender=request.POST.get("gender"),
            password=request.POST.get("password")
        )

        return redirect("login")

    return render(request, "signup.html")


# ---------------- DASHBOARD ----------------

def dashboard(request):

    return render(request, "dashboard.html", {
        "username": "username"
    })


# ---------------- QUIZ ----------------

def quiz(request):

    if request.method == "POST":

        score = 0

        for i in range(1, 10):
            score += int(request.POST.get(f"q{i}", 0))

        request.session["quiz_score"] = score

        return redirect("face")

    return render(request, "quiz.html")


# ---------------- RESULT ----------------

def result(request):

    # Get quiz score
    quiz_score = float(request.session.get("quiz_score", 0))

    # Get face emotion values
    happy = float(request.session.get("happy", 0))
    sad = float(request.session.get("sad", 0))
    neutral = float(request.session.get("neutral", 0))

    # Calculate face emotion score (0–100)
    face_score = (sad * 1.0) + (neutral * 0.25) - (happy * 0.15)

    # Keep score between 0 and 100
    face_score = max(0, min(face_score, 100))

    # Convert face score to PHQ-9 scale (0–27)
    face_quiz_score = (face_score / 100) * 27

    # Final weighted score
    # PHQ-9 = 90%, Face Emotion = 10%
    final_score = round(
        (quiz_score * 0.90) +
        (face_quiz_score * 0.10),
        2
    )

    # Depression Prediction
    if final_score <= 4:
        prediction = "Minimal Depression"

    elif final_score <= 9:
        prediction = "Mild Depression"

    elif final_score <= 14:
        prediction = "Moderate Depression"

    elif final_score <= 19:
        prediction = "Moderately Severe Depression"

    else:
        prediction = "Severe Depression"

    # Send data to results page
    return render(request, "results.html", {
        "quiz_score": round(quiz_score, 2),
        "face_score": round(face_score, 2),
        "final_score": round(final_score, 2),
        "result": prediction,
        "happy": round(happy, 2),
        "sad": round(sad, 2),
        "neutral": round(neutral, 2),
    })


from .face_recognition import decode_image, analyze_frame, calculate_emotion_percentages

# ---------------- FACE PAGE ----------------

def face(request):
    return render(request, "face.html")


# ---------------- ANALYZE FACE ----------------


@csrf_exempt
def analyze_face(request):

    print("🔥 ANALYZE_FACE CALLED")

    if request.method != "POST":
        return JsonResponse({
            "error": "POST request required"
        }, status=400)

    try:

        data = json.loads(request.body)
        image_str = data.get("image", "")

        frame = decode_image(image_str)
        analysis = analyze_frame(frame)

        bbox = analysis.get("bbox")
        if bbox:
            x, y, w, h = bbox
        else:
            x, y, w, h = 0, 0, 0, 0

        happy = analysis["happy"]
        sad = analysis["sad"]
        neutral = analysis["neutral"]
        dominant = analysis["dominant_emotion"]
        confidence = analysis["confidence"]

        print("=" * 50)
        print("Emotion Scores:", analysis["emotions"])
        print("Dominant:", dominant)
        print("=" * 50)

        return JsonResponse({
            "happy": happy,
            "sad": sad,
            "neutral": neutral,
            "emotion": dominant,
            "confidence": confidence,
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "emotions": analysis["emotions"]
        })

    except Exception as e:

        print("analyze_face error:", e)

        return JsonResponse({
            "error": str(e)
        }, status=500)


# ---------------- SAVE FACE RESULT ----------------

@csrf_exempt
def save_face_result(request):

    if request.method == "POST":

        data = json.loads(request.body)

        happy = float(data.get("happy", 0))
        sad = float(data.get("sad", 0))
        neutral = float(data.get("neutral", 0))
        dominant_emotion = data.get("dominant_emotion", "neutral")

        request.session["happy"] = happy
        request.session["sad"] = sad
        request.session["neutral"] = neutral

        face_score = sad + (neutral * 0.3)

        request.session["face_score"] = round(face_score, 2)

        # Save to Database table FaceEmotionResult
        username = request.session.get("username", "Anonymous")
        FaceEmotionResult.objects.create(
            username=username,
            happy=happy,
            sad=sad,
            neutral=neutral,
            dominant_emotion=dominant_emotion
        )

        return JsonResponse({
            "status": "success"
        })

    return JsonResponse({
        "status": "failed"
    })


def journal(request):

    if request.method == "POST":

        mood = request.POST.get("mood")
        stress = request.POST.get("stress")
        energy = request.POST.get("energy")
        sleep = request.POST.get("sleep")
        activities = request.POST.getlist("activity")
        journal_text = request.POST.get("journal")

        DailyLog.objects.create(
            mood=mood,
            stress=stress,
            energy=energy,
            sleep=sleep,
            activities=", ".join(activities),
            journal=journal_text
        )
        messages.success(request, "Daily Log Saved Successfully!")
        return redirect("dashboard")
       

    return render(request, "journal.html")



@csrf_exempt
def nearby_hospitals(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid Request"}, status=400)

    data = json.loads(request.body)

    api_key = settings.GOOGLE_MAPS_API_KEY

    latitude = data.get("latitude")
    longitude = data.get("longitude")
    location = data.get("location")

    # -----------------------------
    # MANUAL LOCATION SEARCH
    # -----------------------------

    if location:

        geo_url = (
            "https://maps.googleapis.com/maps/api/geocode/json"
            f"?address={location}"
            f"&key={api_key}"
        )

        geo = requests.get(geo_url).json()

        print("========== GOOGLE RESPONSE ==========")
        print(geo)
        print("=====================================")

        if geo["status"] != "OK":
            return JsonResponse({
              "error": "Location not found."
         })

        latitude = geo["results"][0]["geometry"]["location"]["lat"]
        longitude = geo["results"][0]["geometry"]["location"]["lng"]

        HospitalSearch.objects.create(
            location=location,
            latitude=latitude,
            longitude=longitude,
            search_type="manual"
        )

    else:

        HospitalSearch.objects.create(
            location="Current Location",
            latitude=latitude,
            longitude=longitude,
            search_type="gps"
        )

    # ------------------------------------
    # SEARCH KEYWORDS
    # ------------------------------------

    keywords = [

        "psychiatrist",

        "psychologist",

        "mental health clinic"

    ]

    hospitals = []
    added = set()

    for keyword in keywords:

        url = (
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={latitude},{longitude}"
            f"&radius=10000"
            f"&keyword={keyword}"
            f"&key={api_key}"
        )

        response = requests.get(url).json()

        if response["status"] not in ["OK", "ZERO_RESULTS"]:
            continue

        for place in response.get("results", []):

            place_id = place.get("place_id")

            if place_id in added:
                continue

            added.add(place_id)

            hospitals.append({

                "name": place.get("name"),

                "rating": place.get("rating", "N/A"),

                "address": place.get("vicinity"),

                "latitude": place["geometry"]["location"]["lat"],

                "longitude": place["geometry"]["location"]["lng"],

                "maps":

                f"https://www.google.com/maps/search/?api=1&query="
                f"{place['geometry']['location']['lat']},"
                f"{place['geometry']['location']['lng']}",

                "direction":

                f"https://www.google.com/maps/dir/?api=1"
                f"&origin={latitude},{longitude}"
                f"&destination="
                f"{place['geometry']['location']['lat']},"
                f"{place['geometry']['location']['lng']}"

            })

    return JsonResponse(hospitals, safe=False)
def hospital_page(request):
    return render(request, "hospital.html")

def information(request):
    return render(request, "information.html")