from djongo import models
from django import forms


class Patient(models.Model):
    name = models.CharField(max_length=70, blank=False, default='')

    def __str__(self):
        return self.name


class BusinessHour(models.Model):
    start = models.TimeField()
    end = models.TimeField()
    closed = models.BooleanField()

    class Meta:
        abstract = True


class BussinessHourForm(forms.ModelForm):
    class Meta:
        model = BusinessHour
        fields = (
            'start', 'end', 'closed'
        )


class MedicalDepartment(models.Model):
    name = models.CharField(max_length=70, blank=False, default='')

    class Meta:
        abstract = True


class MedicalDepartmentForm(forms.ModelForm):
    class Meta:
        model = MedicalDepartment
        fields = (
            'name',
        )


class Doctor(models.Model):
    name = models.CharField(max_length=70, blank=False, default='')
    hospitalName = models.CharField(max_length=70, blank=False, default='')
    medicalDepartment = models.ArrayField(model_container=MedicalDepartment, model_form_class=MedicalDepartmentForm)
    noImbursedMedicalDepartment = models.ArrayField(model_container=MedicalDepartment, model_form_class=MedicalDepartmentForm)
    businessHour = models.ArrayField(model_container=BusinessHour, model_form_class=BussinessHourForm)

    def __str__(self):
        return self.name


class TreatmentRequest(models.Model):
    patientId: models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctorId: models.ForeignKey(Doctor, on_delete=models.CASCADE)
    time: models.DateTimeField()
    createdAt: models.DateTimeField()
    expiredAt: models.DateTimeField()
    isAccepted: models.BooleanField()

