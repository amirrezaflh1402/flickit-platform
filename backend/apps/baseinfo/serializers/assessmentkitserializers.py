from rest_framework import serializers

from assessment.services.assessment_core_services import get_assessment_kit_assessment_count

from baseinfo.models.assessmentkitmodels import AssessmentKit, AssessmentKitDsl, AssessmentKitTag, ExpertGroup, \
    MaturityLevel, LevelCompetence
from baseinfo.models.basemodels import AssessmentSubject, Questionnaire
from rest_framework.validators import UniqueValidator

from baseinfo.serializers import expertgroupserializers
from baseinfo.services import assessmentkitservice


class AssessmentKitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentKitTag
        fields = ['id', 'code', 'title']


class SimpleLevelCompetenceSerilizer(serializers.ModelSerializer):
    maturity_level_id = serializers.IntegerField(source='maturity_level_competence_id')

    class Meta:
        model = LevelCompetence
        fields = ['id', 'value', 'maturity_level_id']


class SimpleMaturityLevelSimpleSerializer(serializers.ModelSerializer):
    level_competences = SimpleLevelCompetenceSerilizer(many=True)

    class Meta:
        model = MaturityLevel
        fields = ['id', 'value', 'level_competences']


class MaturityLevelSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaturityLevel
        fields = ['id', 'title', 'value']


class ExpertGroupSimpleSerilizers(serializers.ModelSerializer):
    class Meta:
        model = ExpertGroup
        fields = ['id', 'name', 'bio', 'about']


class AssessmentKitSerilizer(serializers.ModelSerializer):
    tags = AssessmentKitTagSerializer(many=True)
    expert_group = ExpertGroupSimpleSerilizers()
    number_of_assessment = serializers.SerializerMethodField()
    current_user_is_coordinator = serializers.SerializerMethodField()
    number_of_subject = serializers.SerializerMethodField()
    number_of_questionaries = serializers.SerializerMethodField()
    subjects_with_desc = serializers.SerializerMethodField()
    questionnaires = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()
    maturity_levels = serializers.SerializerMethodField()

    def get_number_of_assessment(self, assessment_kit: AssessmentKit):
        assessment_count_data = get_assessment_kit_assessment_count(assessment_kit_id=assessment_kit.id,
                                                                    total_count=True)
        return assessment_count_data["totalCount"]

    def get_current_user_is_coordinator(self, assessment_kit: AssessmentKit):
        return assessmentkitservice.get_current_user_is_coordinator(assessment_kit,
                                                                    self.context.get('request', None).user.id)

    def get_number_of_subject(self, assessment_kit: AssessmentKit):
        return AssessmentSubject.objects.filter(kit_version=assessment_kit.kit_version_id).all().count()

    def get_number_of_questionaries(self, assessment_kit: AssessmentKit):
        return Questionnaire.objects.filter(kit_version=assessment_kit.kit_version_id).all().count()

    def get_subjects_with_desc(self, assessment_kit: AssessmentKit):
        subjects = AssessmentSubject.objects.filter(kit_version=assessment_kit.kit_version_id).values('id', 'title',
                                                                                                      'description')
        for subject in subjects:
            subj_qs = AssessmentSubject.objects.get(id=subject['id'])
            attributes = subj_qs.quality_attributes.values('id', 'title', 'description')
            subject['attributes'] = attributes
        return subjects

    def get_questionnaires(self, assessment_kit: AssessmentKit):
        return Questionnaire.objects.filter(kit_version=assessment_kit.kit_version_id).values('id', 'title',
                                                                                              'description')

    def get_likes_number(self, assessment_kit: AssessmentKit):
        return assessment_kit.likes.count()

    def get_maturity_levels(self, assessment_kit: AssessmentKit):
        levels = MaturityLevel.objects.filter(kit_version=assessment_kit.kit_version_id).values('id', 'title',
                                                                                                'value')
        for i in range(len(levels)):
            levels[i]["index"] = i + 1
        return levels

    class Meta:
        model = AssessmentKit
        fields = ['id', 'code', 'title', 'summary', 'about', 'tags', 'expert_group',
                  'creation_time', 'last_modification_date', 'likes_number', 'number_of_subject',
                  'number_of_questionaries',
                  'number_of_assessment', 'is_active', 'is_private', 'current_user_is_coordinator',
                  'subjects_with_desc', 'questionnaires', 'maturity_levels']


class AssessmentKitCreateSerilizer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentKit
        fields = ['id']


class UpdateAssessmentKitSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    about = serializers.CharField(required=False)
    summary = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.IntegerField(), required=False)


class LoadAssessmentKitForExpertGroupSerilizer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentKit
        fields = ['id', 'title', "is_private", 'last_modification_date']


class SimpleAssessmentKitTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentKitTag
        fields = ['id', 'title']


class LoadAssessmentKitInfoEditableSerilizer(serializers.ModelSerializer):
    tags = SimpleAssessmentKitTagSerializer(many=True)
    price = serializers.SerializerMethodField('price_value')
    current_user_is_coordinator = serializers.SerializerMethodField()

    def price_value(self, AssessmentKit):
        return 0

    def get_current_user_is_coordinator(self, assessment_kit: AssessmentKit):
        return assessmentkitservice.get_current_user_is_coordinator(assessment_kit,
                                                                    self.context.get('request', None).user.id)

    class Meta:
        model = AssessmentKit
        fields = ['id', 'title', 'summary', 'is_active', 'is_private', 'price', 'about', 'tags',
                  'current_user_is_coordinator']


class SimpleExpertGroupDataForAssessmentKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertGroup
        fields = ['id', 'name']


class SimpleAssessmentSubjectDataForAssessmentKitSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSubject
        fields = ['title']


class LoadAssessmentKitInfoStatisticalSerilizer(serializers.ModelSerializer):
    last_update_time = serializers.DateTimeField(source='last_modification_date')
    questionnaires_count = serializers.SerializerMethodField()
    attributes_count = serializers.SerializerMethodField()
    questions_count = serializers.SerializerMethodField()
    maturity_levels_count = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(source='likes.count')
    assessments_count = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    expert_group = SimpleExpertGroupDataForAssessmentKitSerializer()

    def get_subjects(self, assessment_kit: AssessmentKit):
        data = AssessmentSubject.objects.filter(kit_version=assessment_kit.kit_version_id).values('title')
        return data

    def get_questionnaires_count(self, assessment_kit: AssessmentKit):
        return Questionnaire.objects.filter(kit_version=assessment_kit.kit_version_id).all().count()

    def get_attributes_count(self, assessment_kit: AssessmentKit):
        return AssessmentSubject.objects.filter(kit_version=assessment_kit.kit_version_id).values(
            'quality_attributes').count()

    def get_questions_count(self, assessment_kit: AssessmentKit):
        return Questionnaire.objects.filter(kit_version=assessment_kit.kit_version_id).values('question').count()

    def get_assessments_count(self, assessment_kit: AssessmentKit):
        assessment_count_data = get_assessment_kit_assessment_count(assessment_kit_id=assessment_kit.id,
                                                                    total_count=True)
        return assessment_count_data["totalCount"]

    def get_maturity_levels_count(self, assessment_kit: AssessmentKit):
        return MaturityLevel.objects.filter(kit_version=assessment_kit.kit_version_id).all().count()

    class Meta:
        model = AssessmentKit
        fields = ['creation_time', 'last_update_time', 'questionnaires_count', 'attributes_count', 'questions_count',
                  'maturity_levels_count', 'likes_count', 'assessments_count', 'subjects', 'expert_group']


class EditAssessmentKitInfoSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, min_length=3, max_length=50,
                                  validators=[UniqueValidator(queryset=AssessmentKit.objects.all())])
    about = serializers.CharField(required=False, min_length=3, max_length=1000)
    summary = serializers.CharField(required=False, min_length=3, max_length=200)
    tags = serializers.ListField(child=serializers.IntegerField(), required=False)
    is_active = serializers.BooleanField(required=False)
    is_private = serializers.BooleanField(required=False)
    price = serializers.IntegerField(required=False)


class SimpleAssessmentSubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentSubject
        fields = ['id', 'title', 'index']


class SimpleQuestionnairesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = ['id', 'title', 'index']


class SimpleLoadLevelCompetenceSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="maturity_level_competence.title")
    maturity_level_id = serializers.IntegerField(source='maturity_level_competence_id')

    class Meta:
        model = LevelCompetence
        fields = ['title', 'value', 'maturity_level_id']


class SimpleMaturityLevelSerializer(serializers.ModelSerializer):
    index = serializers.IntegerField(source='value')
    competences = SimpleLoadLevelCompetenceSerializer(source='level_competences', many=True)

    class Meta:
        model = MaturityLevel
        fields = ['id', 'title', 'index', 'competences']


class LoadAssessmentKitDetailsSerializer(serializers.ModelSerializer):
    subjects = serializers.SerializerMethodField()
    questionnaires = serializers.SerializerMethodField()
    maturity_levels = serializers.SerializerMethodField()

    def get_questionnaires(self, assessment_kit: AssessmentKit):
        data = Questionnaire.objects.filter(kit_version=assessment_kit.kit_version_id).order_by('index').values('id', 'title', 'index')
        return data

    def get_subjects(self, assessment_kit: AssessmentKit):
        data = AssessmentSubject.objects.filter(kit_version=assessment_kit.kit_version_id).values('id', 'title',
                                                                                                  'index')
        return data

    def get_maturity_levels(self, assessment_kit: AssessmentKit):
        data = MaturityLevel.objects.filter(kit_version=assessment_kit.kit_version_id)
        return SimpleMaturityLevelSerializer(data, many=True).data

    class Meta:
        model = AssessmentKit
        fields = ['subjects', 'questionnaires', 'maturity_levels']


class LoadAssessmentKitDetailsForReportSerializer(serializers.ModelSerializer):
    maturity_level_count = serializers.SerializerMethodField()
    expert_group = serializers.SerializerMethodField()

    def get_expert_group(self, assessment_kit: AssessmentKit):
        expert_group = assessment_kit.expert_group
        return {"id": expert_group.id, "name": expert_group.name}

    def get_maturity_level_count(self, assessment_kit: AssessmentKit):
        return MaturityLevel.objects.filter(kit_version=assessment_kit.kit_version_id).all().count()

    class Meta:
        model = AssessmentKit
        fields = ['id', 'title', 'summary', 'maturity_level_count', 'expert_group']


class AssessmentKitUpdateSerializer(serializers.Serializer):
    dsl_id = serializers.IntegerField()


class AssessmentKitListSerializer(serializers.ModelSerializer):
    tags = AssessmentKitTagSerializer(many=True)
    expert_group = expertgroupserializers.ExpertGroupAvatarSerializer()
    number_of_assessment = serializers.SerializerMethodField()
    likes_number = serializers.SerializerMethodField()

    def get_number_of_assessment(self, assessment_kit: AssessmentKit):
        assessment_count_data = get_assessment_kit_assessment_count(assessment_kit_id=assessment_kit.id,
                                                                    total_count=True)
        return assessment_count_data["totalCount"]

    def get_likes_number(self, assessment_kit: AssessmentKit):
        return assessment_kit.likes.count()

    class Meta:
        model = AssessmentKit
        fields = ['id', 'title', 'summary', 'tags', 'expert_group', 'likes_number', 'number_of_assessment',
                  'is_private']


class DslSerializer(serializers.Serializer):
    expert_group_id = serializers.IntegerField()
    dsl_file = serializers.FileField()
