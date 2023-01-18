from rest_framework import serializers
from findMyDoctor.models import Doctor, Patient, TreatmentRequest


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
        )


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = (
            'id',
            'hospitalName',
            'medicalDepartment',
            'noImbursedMedicalDepartment',
            'businessHour',
        )


class TreatmentRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRequest
        fields = (
            'id',
            'patientId',
            'doctorId',
            'time',
            'createdAt',
            'expiredAt',
            'isAccepted',
        )