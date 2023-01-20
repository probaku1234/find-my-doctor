from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
import datetime
from .views import BusinessHourViewSet, TreatmentRequestViewSet
from .models import Patient, Doctor, BusinessHour, TreatmentRequest, MedicalDepartment
from freezegun import freeze_time


class TestCaseForBusinessHour(APITestCase):
    def test_create_business_hour(self):
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/business_hour/',
                                       {
                                           'start': datetime.time(9, 0),
                                           'end': datetime.time(18, 0),
                                           'closed': False,
                                       }, format='json')
        business_hour_view = BusinessHourViewSet.as_view({'post': 'create'})
        response = business_hour_view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_should_fail_to_crete_when_start_is_bigger_than_end(self):
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/business_hour/',
                                       {
                                           'start': datetime.time(20, 0),
                                           'end': datetime.time(18, 0),
                                           'closed': False,
                                       }, format='json')
        business_hour_view = BusinessHourViewSet.as_view({'post': 'create'})
        response = business_hour_view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def create_test_business_hour(start, end, closed=False):
    return BusinessHour.objects.create(start=start, end=end, closed=closed)


def create_test_patient(name='test patient'):
    return Patient.objects.create(name=name)


def create_test_doctor(name, hospital_name, times, medical_department=[]):
    doctor = Doctor.objects.create(name=name,
                                   hospitalName=hospital_name,
                                   businessHourMon=times[0],
                                   businessHourTue=times[1],
                                   businessHourWed=times[2],
                                   businessHourThu=times[3],
                                   businessHourFri=times[4],
                                   businessHourSat=times[5],
                                   businessHourSun=times[6],
                                   lunchTime=times[7])
    doctor.medicalDepartment.add(*medical_department)
    return doctor


def create_department(name):
    return MedicalDepartment.objects.create(name=name)


class TestCaseForTreatmentRequest(APITestCase):

    def test_create_treatment_request(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(12, 0), end=datetime.time(1, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/treatment_request', {
            'time': datetime.datetime(2012, 2, 4, 13, 0),
            'patientId': patient.id,
            'doctorId': doctor.id,
        }, format='json')
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'create'
        })
        response = treatment_viewset(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_should_fail_to_create_when_request_time_is_closed(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(12, 0), end=datetime.time(1, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/treatment_request', {
            'time': datetime.datetime(2012, 2, 4, 7, 0),
            'patientId': patient.id,
            'doctorId': doctor.id,
        }, format='json')
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'create'
        })
        response = treatment_viewset(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_should_set_expire_time_20_minutes_later_from_time(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(12, 0), end=datetime.time(1, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/treatment_request', {
            'time': datetime.datetime(2012, 2, 4, 13, 0),
            'patientId': patient.id,
            'doctorId': doctor.id,
        }, format='json')
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'create'
        })
        response = treatment_viewset(request)
        created_at = response.data.serializer.validated_data['createdAt']
        expired_at = response.data['expiredAt']
        delta = expired_at - created_at
        self.assertEqual(delta.seconds, 1200)

    @freeze_time('2012-02-04 9:30:00')
    def test_should_set_expire_time_15_minutes_later_from_time_when_lunch_time(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(9, 0), end=datetime.time(10, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        request_factory = APIRequestFactory()
        # with freeze_time('2012-02-04 12:50:00') as frozen_time:

        request = request_factory.post('/api/treatment_request', {
            'time': datetime.datetime(2012, 2, 4, 12, 30),
            'patientId': patient.id,
            'doctorId': doctor.id,
        }, format='json')
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'create'
        })
        response = treatment_viewset(request)

        expired_at = response.data['expiredAt']
        lunch_date = datetime.datetime.combine(datetime.datetime(expired_at.year, expired_at.month, expired_at.day),
                                               lunch_time.end)
        delta = expired_at - lunch_date

        self.assertEqual(delta.seconds, 900)

    @freeze_time('2012-02-04 11:30:00')
    def test_accept_request(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(9, 0), end=datetime.time(10, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        treatment_request = TreatmentRequest.objects.create(patientId=patient, doctorId=doctor,
                                                            time=datetime.datetime(2012, 2, 4, 13, 0),
                                                            expiredAt=datetime.datetime(2012, 2, 5, 13, 0),
                                                            isAccepted=False)
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/treatment_request/{id}/accept_request'.format(id=treatment_request.id))
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'accept_request'
        })
        response = treatment_viewset(request, pk=treatment_request.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_treatment_request = TreatmentRequest.objects.get(pk=treatment_request.id)

        self.assertEqual(updated_treatment_request.isAccepted, True)

    @freeze_time('2012-02-06 11:30:00')
    def test_should_fail_to_accept_when_its_expired(self):
        patient = create_test_patient()
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(9, 0), end=datetime.time(10, 0), closed=False)

        doctor = create_test_doctor('test doctor', 'test hospital', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ])
        treatment_request = TreatmentRequest.objects.create(patientId=patient, doctorId=doctor,
                                                            time=datetime.datetime(2012, 2, 4, 13, 0),
                                                            expiredAt=datetime.datetime(2012, 2, 5, 13, 0),
                                                            isAccepted=False)
        request_factory = APIRequestFactory()
        request = request_factory.post('/api/treatment_request/{id}/accept_request'.format(id=treatment_request.id))
        treatment_viewset = TreatmentRequestViewSet.as_view({
            'post': 'accept_request'
        })
        response = treatment_viewset(request, pk=treatment_request.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        updated_treatment_request = TreatmentRequest.objects.get(pk=treatment_request.id)

        self.assertEqual(updated_treatment_request.isAccepted, False)


class TestCaseForSearchDoctorByText(APITestCase):
    def create_test_doctors(self):
        business_hour = create_test_business_hour(start=datetime.time(8, 0), end=datetime.time(20, 0),
                                                  closed=False)
        lunch_time = create_test_business_hour(start=datetime.time(12, 0), end=datetime.time(1, 0), closed=False)
        department_1 = create_department('test_department_1')
        department_2 = create_department('test_department_2')
        department_3 = create_department('test_department_3')

        doctor_1 = create_test_doctor('test_doctor_1', 'test_hospital_1', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ], [department_1])
        doctor_2 = create_test_doctor('test_doctor_2', 'test_hospital_2', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ], [department_1, department_2])
        doctor_3 = create_test_doctor('test_doctor_3', 'test_hospital_3', [
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            business_hour,
            lunch_time,
        ], [department_1, department_2, department_3])
        return doctor_1, doctor_2, doctor_3, department_1, department_2, department_3

    def test_should_return_with_matching_name(self):
        doctor_1, doctor_2, doctor_3, _, _, _ = self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_1.name
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], doctor_1.name)

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_2.name
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], doctor_2.name)

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_3.name
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], doctor_3.name)

    def test_should_return_with_matching_hospital(self):
        doctor_1, doctor_2, doctor_3, _, _, _ = self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_1.hospitalName
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hospitalName'], doctor_1.hospitalName)

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_2.hospitalName
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hospitalName'], doctor_2.hospitalName)

        response = self.client.get('/api/doctor/search_by_text', {
            'query': doctor_3.hospitalName
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hospitalName'], doctor_3.hospitalName)

    def test_should_sort_doctor_list_by_matching_level(self):
        doctor_1, doctor_2, doctor_3, department_1, department_2, department_3 = self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_text', {
            'query': '{name} {hospital} {department}'.format(name=doctor_1.name, hospital=doctor_1.hospitalName,
                                                             department=department_1.name)
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]['matching_level'], 3)
        self.assertEqual(response.data[1]['matching_level'], 1)
        self.assertEqual(response.data[2]['matching_level'], 1)

    def test_should_return_empty_list_when_no_matching_data(self):
        self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_text', {
            'query': 'qweqweqwe'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_should_get_all_data_with_no_query(self):
        self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_text')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)


class TestCaseForSearchDoctorByDate(APITestCase):
    def create_test_doctors(self):
        business_hour_1 = create_test_business_hour(start=datetime.time(9, 0), end=datetime.time(18, 0),
                                                    closed=False)
        business_hour_2 = create_test_business_hour(start=datetime.time(11, 0), end=datetime.time(14, 0),
                                                    closed=False)
        no_business = create_test_business_hour(start=datetime.time(11, 0), end=datetime.time(14, 0),
                                                closed=True)
        lunch_time = create_test_business_hour(start=datetime.time(12, 0), end=datetime.time(13, 0), closed=False)

        doctor_1 = create_test_doctor('test_doctor_1', 'test_hospital_1', [
            business_hour_1,
            business_hour_1,
            business_hour_1,
            business_hour_1,
            business_hour_1,
            no_business,
            no_business,
            lunch_time,
        ])
        doctor_2 = create_test_doctor('test_doctor_2', 'test_hospital_2', [
            business_hour_2,
            business_hour_2,
            business_hour_2,
            business_hour_2,
            business_hour_2,
            no_business,
            no_business,
            lunch_time,
        ])

        return doctor_1, doctor_2

    def test_get_doctors_open_at_requested_time(self):
        doctor_1, doctor_2 = self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_date', {
            'requested_time': '2023-01-18 10:00:00'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get('/api/doctor/search_by_date', {
            'requested_time': '2023-01-18 13:10:00'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get('/api/doctor/search_by_date', {
            'requested_time': '2023-01-18 20:10:00'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_should_not_get_doctor_when_request_time_is_in_lunch_time(self):
        doctor_1, doctor_2 = self.create_test_doctors()

        response = self.client.get('/api/doctor/search_by_date', {
            'requested_time': '2023-01-18 12:30:00'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_should_throw_error_when_request_time_missing(self):
        response = self.client.get('/api/doctor/search_by_date')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
