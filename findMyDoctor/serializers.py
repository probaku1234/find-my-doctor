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
    def validate(self, attrs):
        if attrs['start'] > attrs['end']:
            raise serializers.ValidationError('끝 시간은 시작 시간보다 커야합니다')
        return attrs

    class Meta:
        model = BusinessHour
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorFilterSerializer(serializers.ModelSerializer):
    business_hour = serializers.SerializerMethodField()
    medical_department_list = serializers.SerializerMethodField()

    def get_business_hour(self, obj):
        return [
            obj.businessHourMon.to_json(),
            obj.businessHourTue.to_json(),
            obj.businessHourWed.to_json(),
            obj.businessHourThu.to_json(),
            obj.businessHourFri.to_json(),
            obj.businessHourSat.to_json(),
            obj.businessHourSun.to_json(),
            obj.lunchTime.to_json(),
        ]

    def get_medical_department_list(self, obj):
        list = []
        for i in obj.medicalDepartment.all():
            list.append(i.__str__())
        return list
    class Meta:
        model = Doctor
        fields = (
            'id',
            'name',
            'hospitalName',
            'business_hour',
            'medicalDepartment',
            'noImbursedMedicalDepartment',
            'medical_department_list'
        )
def current_time():
    return datetime.now()


class TreatmentRequestSerializer(serializers.ModelSerializer):
    createdAt = serializers.HiddenField(default=current_time)
    expiredAt = serializers.ReadOnlyField(default=datetime.now)
    isAccepted = serializers.ReadOnlyField(default=False)
    patientName = serializers.SerializerMethodField()
    doctorName = serializers.SerializerMethodField()

    def get_patientName(self, obj):
        return obj.patientId.__str__()

    def get_doctorName(self, obj):
        return obj.doctorId.__str__()

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
            raise serializers.ValidationError('끝 시간은 시작 시간보다 커야합니다')

        if attrs['doctorId'].lunchTime.start <= requested_time.time() <= attrs['doctorId'].lunchTime.end:
            raise serializers.ValidationError('끝 시간은 시작 시간보다 커야합니다')

        return super().validate(attrs)

    def create(self, validated_data):
        createdAt = validated_data['createdAt']
        lunchTime = validated_data['doctorId'].lunchTime

        if lunchTime.start <= createdAt.time() <= lunchTime.end:
            expired_at = datetime.combine(datetime(createdAt.year, createdAt.month, createdAt.day),
                                          lunchTime.end) + timedelta(minutes=15)
        else:
            expired_at = createdAt + timedelta(minutes=20)

        validated_data['expiredAt'] = expired_at
        return super().create(validated_data)

    class Meta:
        model = TreatmentRequest
        fields = '__all__'


class TreatmentRequestAcceptSerializer(serializers.ModelSerializer):
    patientId = serializers.PrimaryKeyRelatedField(read_only=True)
    time = serializers.DateTimeField(read_only=True)
    expiredAt = serializers.DateTimeField(read_only=True)
    patientName = serializers.SerializerMethodField()

    def get_patientName(self, obj):
        return obj.patientId.__str__()

    def get_fields(self):
        fields = super().get_fields()
        return fields

    class Meta:
        model = TreatmentRequest
        fields = (
            'id',
            'patientId',
            'time',
            'expiredAt',
            'patientName',
        )
