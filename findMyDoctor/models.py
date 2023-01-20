from django.db import models
from datetime import datetime


class Patient(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=70, blank=False, default='')

    def __str__(self):
        return self.name


class BusinessHour(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    closed = models.BooleanField()

    def __str__(self):
        if self.closed:
            return '휴무'
        else:
            return self.start.__str__() + ' ~ ' + self.end.__str__()

    def to_json(self):
        return {
            'start': self.start,
            'end': self.end,
            'closed': self.closed,
        }
class MedicalDepartment(models.Model):
    name = models.CharField(max_length=70, blank=False, default='')

    def __str__(self):
        return self.name


class Doctor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=70, blank=False, default='')
    hospitalName = models.CharField(max_length=70, blank=False, default='')
    medicalDepartment = models.ManyToManyField(MedicalDepartment, related_name='medicalDepartment', blank=True,
                                               null=True)
    noImbursedMedicalDepartment = models.ManyToManyField(MedicalDepartment, related_name='noImbursedMedicalDepartment',
                                                         blank=True, null=True)
    businessHourMon = models.ForeignKey(BusinessHour, related_name='businessHourMon', on_delete=models.CASCADE,
                                        blank=False)
    businessHourTue = models.ForeignKey(BusinessHour, related_name='businessHourTue', on_delete=models.CASCADE,
                                        blank=False)
    businessHourWed = models.ForeignKey(BusinessHour, related_name='businessHourWed', on_delete=models.CASCADE,
                                        blank=False)
    businessHourThu = models.ForeignKey(BusinessHour, related_name='businessHourThu', on_delete=models.CASCADE,
                                        blank=False)
    businessHourFri = models.ForeignKey(BusinessHour, related_name='businessHourFri', on_delete=models.CASCADE,
                                        blank=False)
    businessHourSat = models.ForeignKey(BusinessHour, related_name='businessHourSat', on_delete=models.CASCADE,
                                        blank=False)
    businessHourSun = models.ForeignKey(BusinessHour, related_name='businessHourSun', on_delete=models.CASCADE,
                                        blank=False)
    lunchTime = models.ForeignKey(BusinessHour, related_name='lunchTime', on_delete=models.CASCADE, blank=False)

    def __str__(self):
        return self.name + ', ' + self.hospitalName


class TreatmentRequest(models.Model):
    id = models.BigAutoField(primary_key=True)
    patientId = models.ForeignKey(Patient, blank=False, on_delete=models.CASCADE, related_name='patientId')
    doctorId = models.ForeignKey(Doctor, blank=False, on_delete=models.CASCADE, related_name='doctorId')
    time = models.DateTimeField(blank=False)
    createdAt = models.DateTimeField(blank=True, auto_now_add=True)
    expiredAt = models.DateTimeField()
    isAccepted = models.BooleanField(blank=False, default=False)
