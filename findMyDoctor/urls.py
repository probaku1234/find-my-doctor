from django.urls import path, include
from findMyDoctor.views import PatientViewSet, DoctorViewSet, TreatmentRequestViewSet, MedicalDepartmentViewSet, \
    BusinessHourViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('patient', PatientViewSet)
router.register('doctor', DoctorViewSet)
router.register('treatment_request', TreatmentRequestViewSet)
router.register('medical_department', MedicalDepartmentViewSet)
router.register('business_hour', BusinessHourViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
