from rest_framework import serializers
from account.models import Space
from account.services import userservices
from account.serializers.commonserializers import UserSimpleSerializer
from assessment.services.assessment_core_services import get_assessment_kit_assessment_count


# from django.db.models.fields import IntegerField

class InputSpaceAccessSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = userservices.load_user_by_email(attrs['email'])
        if user is None or not user.is_active:
            raise serializers.ValidationError()
        return attrs


class InviteMemberSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        user = userservices.load_user_by_email(attrs['email'])
        if user is not None:
            raise serializers.ValidationError({'message': 'An account exists with this email'})
        return attrs


class SpaceListSerializer(serializers.ModelSerializer):
    owner = UserSimpleSerializer()
    members_number = serializers.IntegerField(source='users.count', read_only=True)
    assessment_numbers = serializers.SerializerMethodField(read_only=True)
    def get_assessment_numbers(self, space: Space):
        count_assessmnet = get_assessment_kit_assessment_count(space_id=space.id, not_deleted=True)
        return count_assessmnet["notDeletedCount"]



    class Meta:
        model = Space
        fields = ['id', 'code', 'title', 'last_modification_date', 'owner', 'members_number', 'assessment_numbers']


class SpaceSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ['id', 'code', 'title']
