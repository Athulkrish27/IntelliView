from django.db import models
from administrator.models import Interview_call  # Import the model from administrator


class Interview_application(models.Model):
    application_id = models.AutoField(primary_key=True)
    applied_interview = models.ForeignKey(Interview_call, on_delete=models.CASCADE)
    applicant_name = models.CharField(max_length=100)
    applicant_email = models.CharField(max_length=100)
    applicant_phone = models.CharField(max_length=50)
    applicant_address = models.CharField(max_length=500)
    applicant_resume = models.FileField(upload_to = 'applicant_resume/', null=True)
    applicant_pro_pic = models.ImageField(upload_to = 'profile_pictures/', null=True)
    applicant_face_matrix = models.TextField(null=True)
    applicant_password = models.CharField(max_length=100,null=True)

class Interview_score(models.Model):
    score_id = models.AutoField(primary_key=True)
    score_application = models.ForeignKey(Interview_application, on_delete=models.CASCADE,unique=True)
    score_result = models.IntegerField()
    selected = models.BooleanField(default=False)

