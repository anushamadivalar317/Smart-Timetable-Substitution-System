from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom Member Model
class MemberInfo(AbstractUser):
    USER_TYPES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='teacher')
    created_at = models.DateTimeField(auto_now_add=True)  # Track account creation

    # Full Name Field
    full_name = models.CharField(max_length=200)

    # Additional fields for teachers
    designation = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=50, null=True, blank=True)
    subjects = models.TextField(null=True, blank=True)
    degree = models.CharField(max_length=100, null=True, blank=True)
    certifications = models.FileField(upload_to='certifications/', null=True, blank=True)  # File upload for certificates
    experience = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_staff or self.is_superuser:
            self.user_type = 'admin'
        elif not self.user_type:
            self.user_type = 'teacher'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


# Timetable Model
class Timetable(models.Model):
    teacher = models.ForeignKey(MemberInfo, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    subject = models.CharField(max_length=255)
    classroom = models.CharField(max_length=100)
    time_slot = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.time_slot}"


# Substitute Teacher Model
class Substitute(models.Model):
    absent_teacher = models.ForeignKey(MemberInfo, related_name='absent_teacher', on_delete=models.CASCADE)
    substitute_teacher = models.ForeignKey(MemberInfo, related_name='substitute_teacher', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    schedule_time = models.CharField(max_length=100)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.substitute_teacher} covering {self.absent_teacher} - {self.subject}"


# Attendance Model
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]
    teacher = models.ForeignKey(MemberInfo, on_delete=models.CASCADE, limit_choices_to={'user_type': 'teacher'})
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.teacher.get_full_name()} ({self.teacher.id}) - {self.date} - {self.status}"


# Notification Model
class Notification(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    member = models.ForeignKey(MemberInfo, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.member} - {self.status}"


# Report Model
class Report(models.Model):
    report_type = models.CharField(max_length=255)
    generated_by = models.ForeignKey(MemberInfo, on_delete=models.CASCADE, limit_choices_to={'user_type': 'admin'})
    file_path = models.FileField(upload_to='reports/')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} - {self.generated_by} - {self.generated_at}"



