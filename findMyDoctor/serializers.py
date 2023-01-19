from rest_framework import serializers
from findMyDoctor.models import Doctor, Patient, TreatmentRequest, BusinessHour, MedicalDepartment
from datetime import datetime, timedelta

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = (
            'id',
            'name',
        )


class MedicalDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDepartment
        fields = '__all__'


class BusinessHourSerializer(serializers.ModelSerializer):
    # def validate_empty_values(self, data):
    #     if data['closed']:
    #         return (True, data)
    #     return super().validate_empty_values(data)

    def validate(self, attrs):
        if attrs['start'] > attrs['end']:
            raise serializers.ValidationError('end must after start')
        return attrs

    class Meta:
        model = BusinessHour
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class TreatmentRequestSerializer(serializers.ModelSerializer):
    createdAt = serializers.HiddenField(default=datetime.now)
    expiredAt = serializers.HiddenField(default=datetime.now)
    isAccepted = serializers.HiddenField(default=False)

    def validate(self, attrs):
        business_hour = [
            attrs['doctorId'].businessHourMon,
            attrs['doctorId'].businessHourTue,
            attrs['doctorId'].businessHourWed,
            attrs['doctorId'].businessHourThu,
            attrs['doctorId'].businessHourFri,
            attrs['doctorId'].businessHourSat,
            attrs['doctorId'].businessHourSun,
        ]
        requested_time = attrs['time']
        day = requested_time.weekday()

        if business_hour[day].start > requested_time.time() or requested_time.time() > business_hour[day].end:
            raise serializers.ValidationError('end must after start')

        if attrs['doctorId'].lunchTime.start <= requested_time.time() <= attrs['doctorId'].lunchTime.end:
            raise serializers.ValidationError('end must after start')

        return super().validate(attrs)

    def create(self, validated_data):
        createdAt = validated_data['createdAt']
        lunchTime = validated_data['doctorId'].lunchTime

        if lunchTime.start <= createdAt.time() <= lunchTime.end:
            expired_at = createdAt + timedelta(minutes=15)
        else:
            expired_at = createdAt + timedelta(minutes=20)

        validated_data['expiredAt'] = expired_at
        return super().create(validated_data)

    class Meta:
        model = TreatmentRequest
        fields = '__all__'
