from django.db import models

# Create your models here.

class Interview_call(models.Model):
    interview_id = models.AutoField(primary_key=True)
    interview_post = models.CharField(max_length=200)
    interview_min_quali = models.CharField(max_length=200)
    interview_description = models.CharField(max_length=1000)
    interview_pay_scale = models.CharField(max_length=100)
    interview_syllabus = models.CharField(max_length=200)
    interview_date = models.DateTimeField(auto_now_add=False)
    interview_active = models.BooleanField(default=True)
    interview_finished = models.BooleanField(default=False)
    interview_started = models.BooleanField(default=False)
    
class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_email = models.EmailField(max_length=100)
    admin_password = models.CharField(max_length=30)

class Syllabus(models.Model):
    syllabus_id = models.AutoField(primary_key=True)
    syllabus_name = models.CharField(max_length=200)
    syllabus_file_path = models.FileField(upload_to='syllabus_files/')

class Interview_syllabus_map(models.Model):
    map_id = models.AutoField(primary_key=True)
    map_interview = models.ForeignKey(Interview_call,on_delete=models.CASCADE)
    map_syllabus = models.ForeignKey(Syllabus,on_delete=models.CASCADE)

class Qusetion_answer(models.Model):
    qa_id = models.AutoField(primary_key=True)
    qa_syllabus = models.ForeignKey(Syllabus,on_delete=models.CASCADE)
    qa_q = models.TextField(unique=True)
    qa_a = models.TextField()