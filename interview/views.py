from django.shortcuts import render,redirect
from administrator.models import *
from college.models import Interview_application as Interview_application, Interview_call as Interview_call, Interview_score as Interview_score, models as models
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from PIL import Image
from intelliview.face_scanner import FaceRecognition
from .models import *
import json
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse
import cv2
from administrator.score_predictor import SimilarityScorer


def cur_interview(request):
    interview = Interview_call.objects.get(interview_id = request.session.get("interview_id"))
    return interview

def cur_applicant(request):
    applicant = Interview_application.objects.get(application_id = request.session.get("application_id"))
    return applicant

def interview_home(request):
    now = timezone.now().astimezone()  # Current time in local timezone (Asia/Kolkata if default)
    today = now.date()  # Just the date part (e.g., 2025-04-10)

    interviews = Interview_call.objects.filter(interview_active = True)
    today_interviews = [i for i in interviews if i.interview_date.date() == today]

    return render(request,"interview/interview_home.html",{"interviews":today_interviews,"today":today})


def attend_interview(request,int_id):
    interview = Interview_call.objects.get(interview_id = int_id)
    request.session["interview_id"] = interview.interview_id
    return render(request,"interview/begin_interview.html",{"interview":interview})


def applicant_varification(request):
    interview = cur_interview(request)
    if request.method == "POST":
        email = request.POST.get("email") 
        password = request.POST.get("password")
        try:
            application = Interview_application.objects.get(
                applied_interview=interview.interview_id,
                applicant_email=email,
                applicant_password=password
            )

            # ❗ Check if a score already exists
            if Interview_score.objects.filter(score_application=application).exists():
                return render(request, "interview/begin_interview.html", {"interview": interview,"message": "You have already completed this interview. You cannot attend again."})

            request.session["application_id"] = application.application_id
            if "application_id" not in request.session:
                return redirect('interview_home')
            return redirect("face_verification")
        except:
            return render(request, "interview/begin_interview.html", {"interview": interview,"message": "Could not find your application, check credentials"})

# -----------------------------------------------------------
# Initialize camera globally as None
camera = None

# Function to initialize the camera when needed
def init_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)  # Initialize only when needed

# Generator function to stream video frames
def gen_frames():
    init_camera()  # Initialize the camera when the video feed starts
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Encode frame as JPEG
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # Stream frames as multipart response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    # Release camera after streaming ends
    camera.release()

# View to stream video feed to the live_scan page
def video_feed(request):
    if "application_id" not in request.session:
        return redirect('interview_home')
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def capture_image(request):
    init_camera()
    success, frame = camera.read()
    if success:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_np = np.array(image_pil)

        face_recognizer = FaceRecognition()
        try:
            face_matrix = face_recognizer.get_face_matrix_from_numpy(image_np)
            scanned_face_matrix = face_matrix.tolist()
        except:
            camera.release() # releases the camera if open
            return JsonResponse({
                "status": "No Face found"
            })
        
        applicant = cur_applicant(request)
        applicant_face = applicant.applicant_face_matrix
        face_loaded = json.loads(applicant_face)
        result = face_recognizer.compare_faces(scanned_face_matrix, face_loaded)

        if result:
            camera.release()  # releases the camera if open
            return JsonResponse({
                "status": "Face Verified",
                "redirect_url": reverse("session2")
            })

    camera.release() # releases the camera if open
    return JsonResponse({
        "status": "Face Not Verified"
    })


@csrf_exempt
def face_verification(request):
    if "application_id" not in request.session:
        return redirect('interview_home')
    return render(request, "interview/face_verification.html")

def session2(request):
    if "application_id" not in request.session:
        return redirect('interview_home')
    applicant = cur_applicant(request)
    return render(request,"interview/session2.html",{"applicant":applicant})

def introduce_yourself(request):
    if "application_id" not in request.session:
        return redirect('interview_home')
    return render(request,"interview/introduce_yourself.html")



def session3(request):

    if "application_id" not in request.session:
        return redirect('interview_home')

    camera.release()
    interview = cur_interview(request)  # Get current Interview_call object
    interview_score = Interview_score()
    interview_score.score_application = cur_applicant(request)

    # Step 1: Get all syllabus IDs linked to this interview
    mapped_syllabus_ids = Interview_syllabus_map.objects.filter(map_interview=interview).values_list('map_syllabus__syllabus_id', flat=True)

    # Step 2: Get all related question-answer objects (random 10)
    questions = Qusetion_answer.objects.filter(qa_syllabus__syllabus_id__in=mapped_syllabus_ids).order_by('?')[:10]

    score = None  # Default

    if request.method == "POST":
        submitted_answers = []
        actual_answers = [q.qa_a for q in questions]  # Original correct answers
        scorer = SimilarityScorer()

        # Step 3: Loop through each question index
        for i in range(1, 11):
            key = f'answer{i}'
            answer = request.POST.get(key, "Nothing").strip()
            if answer == "":
                answer = "Nothing"
            submitted_answers.append(answer)

        # Step 4: Compute similarity scores
        total_score = 0
        for submitted, actual in zip(submitted_answers, actual_answers):
            total_score += scorer.score(actual, submitted)

        score = round(total_score / len(questions), 2)  # Average score out of 100
        print(f"------------------------------  {score} ")
        interview_score.score_result = score
        try:
            interview_score.save()
        except:
            return redirect("interview_home")
        
        request.session.pop("application_id", None)
        request.session.pop("interview_id", None)
        return render(request,"interview/completed.html")
    

    return render(
        request,
        "interview/session3_questions.html",
        {
            "questions": questions,
            "interview": interview,
            "score": score  # Pass to template
        }
    )
