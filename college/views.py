from django.shortcuts import render,redirect
from django.db.utils import IntegrityError
from django.conf import settings
from administrator.models import Interview_call
from .models import *
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
import PIL
from .face_scaner import FaceRecognition
import random
import string
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def college_home(request):
    return render(request,"college/college_home.html",{"message":""})

def career_page(request):
    interview_calls = Interview_call.objects.filter(interview_active=True, interview_started = False)
    return render(request,"college/career_page.html",{"cards":interview_calls,"message":""})

def collect_email(request,interview_id):
    request.session["cur_interview_id"] = interview_id
    return render(request,"college/collect_email.html")

def apply_interview(request,interview_id):
    return render(request,"college/apply_interview.html",{"interview_id":interview_id})

def generate_strong_password(length=8):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choices(characters, k=length))
    return password


def send_otp(request):
    otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP

    request.session['otp'] = otp  # Store in session
    request.session['email'] = request.POST.get("email")  # Store the email for validation

    sender_email = settings.EMAIL_HOST_USER
    app_password = settings.EMAIL_HOST_PASSWORD

    if not app_password:
        return render(request, "college/collect_email.html", {
            "message": "Email configuration is missing. Set EMAIL_HOST_PASSWORD in environment."
        })
    
    subject = "IntelliviewSystem: Email Verification"
    body = f"Your OTP is: {otp}\n\nPlease enter this code to verify your identity."

    receiver_email = request.POST.get("email")

    # Create email message
    msg = MIMEText(body)
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    try:
        # Setup SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return render(request,"college/varify_otp.html",{"message":"OTP Sent"})
    
    except :
        return render(request,"college/collect_email.html",{"message":"Could not send OTP"})

def verify_otp(request):
    given_otp = request.POST.get("given_otp")
    try:
        existing_otp = request.session.get("otp")
        if existing_otp == given_otp:
            email = request.session.get("email")
            interview_id = request.session.get("cur_interview_id")

            del request.session['otp'] # clearing otp
            del request.session['email'] # clearing email
            del request.session['cur_interview_id'] # clearing email
            return render(request,"college/apply_interview.html",{"interview_id":interview_id,"email":email,"message":"Verification Successful"})
        else:
            return render(request,"college/varify_otp.html",{"message":"OTP Not Matching"})
    except:
        return render(request,"college/collect_email.html",{"message":"Could not verify OTP"})


def send_mail(receiver_email,jobpost,date,password):

    # Setup SMTP server
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    app_password = settings.EMAIL_HOST_PASSWORD

    if not app_password:
        raise ValueError("Email password not configured. Set EMAIL_HOST_PASSWORD in environment.")

    # Login
    server.login(settings.EMAIL_HOST_USER, app_password)

    # Email details
    sender_email = settings.EMAIL_HOST_USER
    sender_name = "IntelliView Admin"  # This name will be displayed

    # Create email message with headers
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"  # Sets custom sender name
    msg["To"] = receiver_email
    msg["Subject"] = "Job Application Accepted"

    # Email body in HTML format

    interview_address = "Example place, example address."
    contact_info = "0468 222350"

    body = f"""
    <html>
    <head>
        <style>
            .password {{
                font-size: 20px;
                font-weight: bold;
                color: red;
            }}
        </style>
    </head>
    <body>
        <p>Dear Candidate,</p>

        <p>We are pleased to inform you that your application for the position of <b>{jobpost}</b> has been successfully accepted. You are required to be present at the interview center on <b>{date}</b>, carrying the necessary documents to verify your identity and professional experience.</p>

        <p><b>🔐 Important: Your application password is:</b></p>
        <p class="password">{password}</p>
        <p><b>This password is required to attend the interview. Please do not share it with anyone.</b></p>

        <hr>

        <p><b>Interview Details:</b></p>
        <ul>
            <li><b>Position Applied For:</b> {jobpost}</li>
            <li><b>Interview Date:</b> {date}</li>
            <li><b>Interview Location:</b> {interview_address}</li>
            <li><b>Contact for Assistance:</b> {contact_info}</li>
        </ul>

        <hr>

        <p>The interview will be conducted through an AI-assisted computer system. Any attempt to manipulate or violate the integrity of the assessment will result in immediate disqualification.</p>

        <p>We advise you to prepare thoroughly and arrive on time. Wishing you the very best for your interview.</p>

        <p>Best regards,<br>
        <b>IntelliView Recruitment Team</b></p>
    </body>
    </html>
    """


    msg.attach(MIMEText(body, "html"))

    # Send the email
    server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Done")
    # Close connection
    server.quit()


def submit_application(request):
    
    if request.method == "POST":
        try:
            interview_id = request.POST.get("interview_id")

            # Check if already applied
            is_applied = Interview_application.objects.filter(
                applicant_email=request.POST.get("email"),
                applied_interview=interview_id
            ).exists()

            if is_applied:
                return render(request, "college/collect_email.html", {
                    "message": "Application Failed! Already applied with this email"
                })

            # Get interview object
            interview_call = Interview_call.objects.get(interview_id=interview_id)

            # Create object
            table = Interview_application()
            table.applied_interview = interview_call
            table.applicant_name = request.POST.get("name")
            table.applicant_email = request.POST.get("email")
            table.applicant_phone = request.POST.get("phone")
            table.applicant_address = request.POST.get("address")

            # Save files
            table.applicant_resume = request.FILES.get('resume')
            pro_pic_file = request.FILES.get('pro_pic')

            if not pro_pic_file:
                return render(request, "college/collect_email.html", {
                    "message": "Please upload a profile picture"
                })

            table.applicant_pro_pic = pro_pic_file

            # ✅ FIXED IMAGE PROCESSING
            image_pil = Image.open(pro_pic_file)
            image_pil = image_pil.convert("RGB")  # Important
            image_np = np.array(image_pil)

            # Face recognition
            face_recognizer = FaceRecognition()
            face_matrix = face_recognizer.get_face_matrix_from_numpy(image_np)

            # ✅ Face check
            if face_matrix is None:
                return render(request, "college/collect_email.html", {
                    "message": "No face detected. Please upload a clear, close-up image."
                })

            # Save face data
            table.applicant_face_matrix = face_matrix.tolist()

            # Generate password
            password = generate_strong_password()
            table.applicant_password = password

            # Save application
            table.save()

            # Format date & time
            date = interview_call.interview_date
            formatted_date = date.strftime("%d-%m-%Y")
            formatted_time = date.strftime("%I:%M %p")
            formatted_datetime = f"{formatted_date} at {formatted_time}"

            # Send mail
            send_mail(
                receiver_email=request.POST.get("email"),
                jobpost=interview_call.interview_post,
                date=formatted_datetime,
                password=password
            )

            return render(request, "college/college_home.html", {
                "message": "Application submitted successfully"
            })

        except Exception as e:
            print("ERROR:", e)  # 🔥 VERY IMPORTANT for debugging

            return render(request, "college/collect_email.html", {
                "message": f"Application Failed! {str(e)}"
            })

    return render(request, "college/collect_email.html", {"message": ""})