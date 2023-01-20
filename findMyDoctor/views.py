from datetime import datetime
import moment

from django.utils import timezone

from rest_framework import status
import django_filters.rest_framework
from django_filters import rest_framework as filters
from findMyDoctor.models import Patient, Doctor, TreatmentRequest, MedicalDepartment
from findMyDoctor.serializers import PatientSerializer, DoctorSerializer, TreatmentRequestSerializer, \
    MedicalDepartmentSerializer, BusinessHour, BusinessHourSerializer, TreatmentRequestAcceptSerializer, \
    DoctorFilterSerializer

from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from itertools import filterfalse


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class DoctorFilter(filters.FilterSet):
    date = filters.DateTimeFilter(method='filter_timestamp', field_name='pika')

    class Meta:
        model = Doctor
        fields = '__all__'

    def filter_timestamp(self, queryset, name, value):
        return queryset.filter(**{name: value})


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = DoctorFilter

    def list(self, request, *args, **kwargs):
        return super().list(request, args, kwargs)


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


def is_time_within_business_hour(data, date):
    day = date.weekday

    if data['business_hour'][day]['closed']:
        return True

    lunch_start = data['business_hour'][7]['start']
    lunch_end = data['business_hour'][7]['end']
    lunch_start = moment.date(date.year, date.month, date.day).add(hours=lunch_start.hour, minutes=lunch_start.minute,
                                                                   seconds=lunch_start.second)
    lunch_end = moment.date(date.year, date.month, date.day).add(hours=lunch_end.hour, minutes=lunch_end.minute,
                                                                 seconds=lunch_end.second)
    if date.__ge__(lunch_start) and date.__le__(lunch_end):
        return True

    business_start = data['business_hour'][day]['start']
    business_end = data['business_hour'][day]['end']
    business_start = moment.date(date.year, date.month, date.day).add(hours=business_start.hour,
                                                                      minutes=business_start.minute,
                                                                      seconds=business_start.second)
    business_end = moment.date(date.year, date.month, date.day).add(hours=business_end.hour,
                                                                    minutes=business_end.minute,
                                                                    seconds=business_end.second)
    if date.__ge__(moment.date(business_start)) and date.__le__(moment.date(business_end)):
        return False

    return True


@api_view(['GET'])
def search_doctor_by_time(request):
    query_date = request.query_params.get('requested_time')
    if not query_date:
        return Response(data='파라미터 requested_time가 필요합니다', status=status.HTTP_400_BAD_REQUEST)

    try:
        moment.date(request.query_params.get('requested_time'))
    except ValueError:
        return Response(data='형식에 맞지 않는 requested_time 값입니다', status=status.HTTP_400_BAD_REQUEST)

    requested_time = moment.date(request.query_params.get('requested_time'))
    doctors = Doctor.objects.all()
    doctors_serializer = DoctorFilterSerializer(doctors, many=True)

    filtered_data = list(
        filterfalse(lambda x: is_time_within_business_hour(x, requested_time), doctors_serializer.data))

    return Response(filtered_data)


def get_matching_level(data, keywords):
    matching_name = 0
    matching_hospital = 0
    matching_department = 0

    for keyword in keywords:
        if not matching_name:
            if keyword == data['name']:
                matching_name = 1
                continue

        if not matching_hospital:
            if keyword == data['hospitalName']:
                matching_hospital = 1
                continue

        if not matching_department:
            if keyword in data['medical_department_list']:
                matching_department = 1
                continue

    return matching_name + matching_department + matching_hospital


@api_view(['GET'])
def search_doctor_by_text(request):
    doctors = Doctor.objects.all()
    doctors_serializer = DoctorFilterSerializer(doctors, many=True)

    query_string = request.query_params.get('query')
    if not query_string:
        return Response(data=doctors_serializer.data)
    keywords = query_string.split()

    matching_doctors_list = []

    for doctor in doctors_serializer.data:
        matching_level = get_matching_level(doctor, keywords)

        if matching_level:
            doctor['matching_level'] = matching_level
            matching_doctors_list.append(doctor)

    matching_doctors_list.sort(key=lambda e: e['matching_level'], reverse=True)

    return Response(data=matching_doctors_list, status=status.HTTP_200_OK)
