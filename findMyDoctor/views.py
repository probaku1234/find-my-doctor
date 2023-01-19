from datetime import datetime

from django.shortcuts import render
from django.utils import timezone
from rest_framework.response import Response
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
import django_filters.rest_framework

from findMyDoctor.models import Patient, Doctor, TreatmentRequest, MedicalDepartment
from findMyDoctor.serializers import PatientSerializer, DoctorSerializer, TreatmentRequestSerializer, \
    MedicalDepartmentSerializer, BusinessHour, BusinessHourSerializer, TreatmentRequestAcceptSerializer

from rest_framework.decorators import action
from rest_framework import viewsets


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    # http_method_names = ['get', 'post', 'head']


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class TreatmentRequestViewSet(viewsets.ModelViewSet):
    queryset = TreatmentRequest.objects.all()
    serializer_class = TreatmentRequestSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['doctorId', 'isAccepted']

    @action(detail=True, methods=['POST'], name='accept-request', serializer_class=TreatmentRequestAcceptSerializer)
    def accept_request(self, request, pk=None):
        treatment_request = TreatmentRequest.objects.get(pk=pk)

        if timezone.make_aware(datetime.now()) > treatment_request.expiredAt:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        treatment_request.isAccepted = True
        treatment_request.save()

        return Response(status=status.HTTP_200_OK)




class MedicalDepartmentViewSet(viewsets.ModelViewSet):
    queryset = MedicalDepartment.objects.all()
    serializer_class = MedicalDepartmentSerializer


class BusinessHourViewSet(viewsets.ModelViewSet):
    queryset = BusinessHour.objects.all()
    serializer_class = BusinessHourSerializer
