from django.shortcuts import render,redirect
from .models import *
from college.models import *
from django.utils import timezone
from datetime import datetime
from .quizz_master import QuestionAnswerProcessor  # custom class
from django.urls import reverse
from django.contrib import messages
from college.models import Interview_application
from django.views.decorators.cache import cache_control, never_cache
from pytz import timezone as pytz_timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import smtplib
from django.utils.timezone import localtime
from django.utils.http import urlencode

# ---------------------------------------

# table = Admin()
# table.admin_email="admin@gmail.com"
# table.admin_password = "admin"
# table.save()

# ---------------------------------------


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_home(request):
    if request.session.get("admin_id"):  # checking for logged in accounts
        interview_count = Interview_call.objects.filter(interview_active=True).count()
        application_count = Interview_application.objects.count()
        syllabus_count = Syllabus.objects.count()
        qa_count = Qusetion_answer.objects.count()
        return render(request,"admin/admin_home.html",{"interview_count":interview_count ,"application_count":application_count,"syllabus_count":syllabus_count,"qa_count":qa_count})
    else:
        return redirect(admin_login)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_logout(request):
    del request.session["admin_id"]
    return redirect(admin_home)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email") 
        password = request.POST.get("password")
        try:
            accounts = Admin.objects.get(admin_email=email,admin_password=password)
            request.session["admin_id"] = accounts.admin_id
            return redirect(admin_home)
        except:
            return render(request,"admin/login.html",{"message":"Could not login!"})
    return render(request,"admin/login.html")
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_interview(request):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    if request.method == "POST":
        table = Interview_call()
        try:
            table.interview_post = request.POST.get("title")
            table.interview_min_quali = request.POST.get("qualification")
            table.interview_pay_scale = request.POST.get("pay_scale")  
            table.interview_syllabus = request.POST.get("syllabus")
            table.interview_description = request.POST.get("description")

            # Get the input datetime string and convert it to timezone-aware datetime
            date_str = request.POST.get("date")
            interview_date_naive = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            india_timezone = pytz_timezone("Asia/Kolkata")
            table.interview_date = india_timezone.localize(interview_date_naive)

            table.save()
            return redirect(view_interview)
        
        except:
            return render(request, "admin/create_interview.html", {"message": f"Could not schedule interview: Try again!"})

    return render(request, "admin/create_interview.html", {"message": ""})


def send_mail(receiver_email,jobpost,date):

    # Setup SMTP server
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    # App Password
    app_password = "khmy pvqi tqkn mnup"

    # Login
    server.login("intelliviewadmi@gmail.com", app_password)

    # Email details
    sender_email = "intelliviewadmi@gmail.com"
    sender_name = "IntelliView Admin"  # This name will be displayed

    # Create email message with headers
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"  # Sets custom sender name
    msg["To"] = receiver_email
    msg["Subject"] = "Interview Got Cancelled"

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

        <p>We regret to inform you that your scheduled interview for the position of <b>{jobpost}</b>, originally planned for <b>{date}</b>, has been <span style="color:red;"><b>cancelled</b></span>.</p>

        <p>This cancellation may be due to administrative reasons, scheduling conflicts, or unforeseen circumstances. We sincerely apologize for any inconvenience this may cause.</p>

        <hr>

        <p><b>Cancelled Interview Details:</b></p>
        <ul>
            <li><b>Position Applied For:</b> {jobpost}</li>
            <li><b>Scheduled Date:</b> {date}</li>
            <li><b>Interview Location:</b> {interview_address}</li>
            <li><b>Contact for Assistance:</b> {contact_info}</li>
        </ul>

        <hr>

        <p>If this interview is to be rescheduled, you will be notified with a new invitation and instructions. Meanwhile, if you have any questions or require further clarification, please feel free to contact our support team.</p>

        <p>Thank you for your understanding.</p>

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





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_interview(request,int_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    table = Interview_call.objects.get(interview_id = int_id)
    syllabuses = Syllabus.objects.all()
    connected_syl = Interview_syllabus_map.objects.filter(map_interview = int_id)
    is_today = table.interview_date.date() == timezone.now().date()
    return render(request, "admin/edit_interview.html", {"interview":table,"syllabuses":syllabuses,"connected_syl":connected_syl,"is_today":is_today})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_interview(request,int_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    table = Interview_call.objects.get(interview_id = int_id)
    if request.method == "POST":
        try:
            table.interview_post = request.POST.get("title")
            table.interview_min_quali = request.POST.get("qualification")
            table.interview_pay_scale = request.POST.get("pay_scale")  
            table.interview_syllabus = request.POST.get("syllabus")
            table.interview_description = request.POST.get("description")

            # Convert date to a timezone-aware datetime object
            date_str = request.POST.get("date")  # This is a string (e.g., "2025-02-20T23:28")
            interview_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")  # Convert to datetime
            table.interview_date = timezone.make_aware(interview_date)  # Make it timezone-aware

            table.save()
            messages.success(request, "Interview details updated successfully!")
            return redirect(view_interview)

        except:
            return redirect("edit_interview",int_id=int_id)
        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_syl_interview_map(request,int_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    map_exists = Interview_syllabus_map.objects.filter(map_interview = int_id,map_syllabus = request.POST.get("syllabus_id")).exists()

    if not map_exists:
        interview = Interview_call.objects.get(interview_id=int_id)
        syllabus = Syllabus.objects.get(syllabus_id = request.POST.get("syllabus_id"))
        table = Interview_syllabus_map()

        table.map_interview = interview
        table.map_syllabus = syllabus
        table.save()
    return redirect("edit_interview", int_id=int_id)
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def remove_syl_interview_map(request,int_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    interview = Interview_call.objects.get(interview_id=int_id)
    syllabus = Syllabus.objects.get(syllabus_id = request.POST.get("syllabus_id"))
    table = Interview_syllabus_map.objects.get(map_interview = interview, map_syllabus = syllabus)

    table.delete()

    return redirect("edit_interview", int_id=int_id)
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_interview(request):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    interviews = Interview_call.objects.filter(interview_active = True).order_by("-interview_id")
    return render(request,"admin/view_interview.html",{"interviews":interviews})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_syllabus(request):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    if request.method == "POST":
        table = Syllabus()
        try:
            table.syllabus_name = request.POST.get("title")
            table.syllabus_file_path = request.FILES['file']

            table.save()
            return redirect(view_syllabus)
        
        except:
            return render(request, "admin/add_syllabus.html", {"message": f"Could not add syllabus: Try again!"})

    return render(request, "admin/add_syllabus.html")

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_syllabus(request):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    syllabuses = Syllabus.objects.all().order_by("-syllabus_id")
    return render(request,"admin/view_syllabus.html",{"syllabuses":syllabuses})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def syllabus_action(request,syl_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    syllabus = Syllabus.objects.get(syllabus_id=syl_id)
    q_a = Qusetion_answer.objects.filter(qa_syllabus = syl_id).order_by("-qa_id") # questions and answers
    return render(request,"admin/syllabus_action.html",{"syllabus":syllabus,"qa_s":q_a})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generate_qa(request):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    processor = QuestionAnswerProcessor()
    if request.method=="POST":
        syl_id = request.POST.get("syl_id")
        syllabus = Syllabus.objects.get(syllabus_id=syl_id)
        num_questions = int(request.POST.get("num_ques"))
        qa_data = processor.process_pdf(syllabus.syllabus_file_path, num_questions)

        # save each q and a into the database
        for ques,ans in qa_data.items():
            print(f"{ques} ::::::: {ans}")
            table = Qusetion_answer()
            try:  # chance of getting an existing question
                table.qa_syllabus = syllabus
                table.qa_q = ques
                table.qa_a = ans
                table.save()
            except:
                print(f"----------------- exception -------------")
                continue
        return redirect(reverse('syllabus_action', kwargs={'syl_id': str(syl_id)}))

    return redirect(reverse('view_syllabus'))

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_qa(request,qa_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    qa = Qusetion_answer.objects.get(qa_id=qa_id)
    if request.method=="POST":
        qa.qa_q = request.POST.get("question")
        qa.qa_a = request.POST.get("answer")
        qa.save()
        syllabuses = Syllabus.objects.all().order_by("-syllabus_id")
        return render(request,"admin/view_syllabus.html",{"syllabuses":syllabuses,"message":"Changes saved succesfully!"})

    return render(request, "admin/manage_qa.html",{"qa":qa})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cancel_interview(request,int_id):
    if "admin_id" not in request.session:
        return redirect('admin_login')
    interview = Interview_call.objects.get(interview_id = int_id)
    if interview.interview_active:
        interview.interview_active = False
        interview.save()

        candidates = Interview_application.objects.filter(applied_interview = int_id)
        date = interview.interview_date  
        # Format the date and time
        formatted_date = date.strftime("%d-%m-%Y")  # Example: 29-03-2025
        formatted_time = date.strftime("%I:%M %p")  # Example: 02:30 PM
        # Final output
        formatted_datetime = f"{formatted_date} at {formatted_time}"

        for cand in candidates:
            send_mail(receiver_email=cand.applicant_email,jobpost=interview.interview_post,date=formatted_datetime)

    syllabuses = Syllabus.objects.all()
    connected_syl = Interview_syllabus_map.objects.filter(map_interview = int_id)
    return render(request, "admin/view_interview.html", {"interview":interview,"syllabuses":syllabuses,"connected_syl":connected_syl,"message":"Interview has been cancelled and informed all applicants"})

def start_interview(request,int_id):
    interview = Interview_call.objects.get(interview_id = int_id)
    if not interview.interview_started :
        interview.interview_started = True
        interview.save()
    return redirect("edit_interview",int_id=int_id)

def finish_interview(request,int_id):
    interview = Interview_call.objects.get(interview_id = int_id)
    if not interview.interview_finished :
        interview.interview_finished = True
        interview.save()
    return redirect("edit_interview",int_id=int_id)


def see_result(request, int_id):
    interview = Interview_call.objects.get(interview_id=int_id)
    applications = Interview_application.objects.filter(applied_interview=interview).select_related()

    candidates = []
    for app in applications:
        try:
            score = Interview_score.objects.get(score_application=app)
            candidates.append({
                'applicant_name': app.applicant_name,
                'applicant_email': app.applicant_email,
                'applicant_phone': app.applicant_phone,
                'applicant_resume': app.applicant_resume,
                'applicant_pro_pic': app.applicant_pro_pic,
                'interview_score': score,
                'selected': score.selected,
                'application_id': app.application_id  # <-- Add this line
            })
        except Interview_score.DoesNotExist:
            continue

    candidates = sorted(candidates, key=lambda x: x['interview_score'].score_result, reverse=True)

    # Get message from query parameter if exists
    message = request.GET.get("message", "")

    return render(request, "admin/see_result.html", {
        "candidates": candidates,
        "interview": interview,
        "message": message
    })


def send_selection_email(receiver_email, candidate_name, jobpost, date):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        sender_email = "intelliviewadmi@gmail.com"
        app_password = "khmy pvqi tqkn mnup"
        sender_name = "IntelliView Admin"

        server.login(sender_email, app_password)

        # Email details
        subject = f"🎉 You're Selected for {jobpost} Interview at IntelliView!"
        contact_info = "+91 468 222350 | support@intelliview.com"

        body = f"""
        <html>
        <head>
            <style>
                .highlight {{ font-weight: bold; color: #2c3e50; font-size: 18px; }}
            </style>
        </head>
        <body>
            <p>Dear <b>{candidate_name}</b>,</p>

            <p>We are pleased to inform you that you have been <span class="highlight">selected</span> in the interview conducted on <span class="highlight">{date}</span> for the post of <span class="highlight">{jobpost}</span> with IntelliView.</p>

            <p>Our HR team will reach out to you soon for further steps.</p>

            <hr>
            <p><b>Contact:</b> {contact_info}</p>
            <hr>

            <p>Congratulations once again, and we look forward to working with you!</p>

            <p>Best wishes,<br>
            <b>IntelliView Recruitment Team</b></p>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        print("❌ Email sending failed:", str(e))
        return False


def select_candidate(request, app_id):
    application = Interview_application.objects.get(application_id=app_id)
    interview = application.applied_interview
    score = Interview_score.objects.get(score_application=application)
    formatted_date = localtime(interview.interview_date).strftime("%B %d, %Y at %I:%M %p")

    email_sent = send_selection_email(
        receiver_email=application.applicant_email,
        candidate_name=application.applicant_name,
        jobpost=interview.interview_post,
        date=formatted_date,
    )

    # If email sent → mark selected and save
    if email_sent:
        score.selected = True
        score.save()
        message = "✅ Candidate has been selected and notified via email."
    else:
        message = "❌ Failed to send selection email. Candidate was not selected."

    # Redirect with message as query param
    base_url = reverse("see_result", kwargs={"int_id": interview.interview_id})
    query_string = urlencode({"message": message})
    url = f"{base_url}?{query_string}"
    return redirect(url)