from rest_framework import serializers

from .models import Course, StudyMaterial, Lesson, Card, Tag, EnumConfig, Survey, Question, UserResponse, \
    CourseScheduleContent, CardStudyMaterial
from .models import TermCourse, CourseScheduleStudent, UserStudyRecord


class CourseSerializer(serializers.ModelSerializer):
    """
    课程序列化
    """
    type_description = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_type_description(self, obj):
        # 调用Course模型中的type_description属性
        return obj.type_description


class LessonListSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    type_description = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_type_description(self, obj):
        # 调用Course模型中的type_description属性
        return obj.type_description


class CardListSimpleSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """
    type_description = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'title', 'type_description']

    def get_type_description(self, obj):
        return obj.type_description


class CardListSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """
    type_description = serializers.SerializerMethodField()
    difficulty_description = serializers.SerializerMethodField()
    status_description = serializers.SerializerMethodField()
    study_materials = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = '__all__'

    # def create(self, validated_data):
    #     # 在创建时自动添加一个字段
    #     validated_data['some_field'] = '自动添加的值'
    #     # 调用父类的 create 方法来创建模型实例
    #     return super(CardListSerializer, self).create(validated_data)
    #
    # def update(self, instance, validated_data):
    #     # 在更新时自动修改一个字段
    #     instance.study_material_ids = validated_data.get('study_material_ids', [1,2,3])
    #     # 调用父类的 update 方法来更新模型实例
    #     return super(CardListSerializer, self).update(instance, validated_data)

    def get_study_materials(self, obj):
        _card_study_materials = CardStudyMaterial.objects.filter(card=obj.id).values_list('studymaterial__id', flat=True).all()
        return _card_study_materials

    # def get_study_materials(self, obj):
    #     # 由于这里只是一个卡片对象，Prefetch不会直接在这里生效
    #     # 但是在视图集的get_queryset中可以使用Prefetch来优化查询
    #     return [sm.studymaterial_id for sm in obj.cardstudymaterial_set.all()]

    def get_type_description(self, obj):
        return obj.type_description

    def get_difficulty_description(self, obj):
        return obj.difficulty_description

    def get_status_description(self, obj):
        return obj.status_description


class TagSerializer(serializers.ModelSerializer):
    """
    标签序列号
    """

    class Meta:
        model = Tag
        fields = '__all__'


class TagDetailSerializer(serializers.ModelSerializer):
    """
    标签序列号
    """

    class Meta:
        model = Tag
        fields = ['id', 'name', 'create_time']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    type_description = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'sub_title', 'description', 'type_description', 'type', 'context', 'tags',
                  'create_time', 'update_time']

    def get_type_description(self, obj):
        return obj.type_description


class StudyMaterialSimpleListSerializer(serializers.ModelSerializer):
    type_description = serializers.SerializerMethodField()

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'type_description', 'type']

    def get_type_description(self, obj):
        return obj.type_description


class EnumConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnumConfig
        fields = '__all__'


class StudyMaterialDetailSerializer(serializers.ModelSerializer):
    tags = TagDetailSerializer(many=True, read_only=True)

    class Meta:
        model = StudyMaterial
        fields = ['id', 'title', 'sub_title', 'description', 'type', 'context', 'tags']


class CardDetailSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """
    study_materials = StudyMaterialDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = '__all__'


class CardDetailSimpleSerializer(serializers.ModelSerializer):
    """
    卡片序列号
    """
    study_materials = StudyMaterialSimpleListSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = '__all__'


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    cards = CardListSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    survey_info = SurveySerializer(source='survey', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class UserResponseSerializer(serializers.ModelSerializer):
    survey_info = SurveySerializer(source='survey', read_only=True)
    question_info = QuestionListSerializer(source='question', read_only=True)

    class Meta:
        model = UserResponse
        # fields = ['id', 'survey_title', 'question_text', 'answer', 'response_time', 'update_time', 'create_time']
        fields = '__all__'


class TermCourseDetailSerializer(serializers.ModelSerializer):
    course_info = CourseSerializer(read_only=True, source='course')

    class Meta:
        model = TermCourse
        fields = '__all__'


class TermCourseSerializer(serializers.ModelSerializer):
    # course_info = CourseSerializer(read_only=True, source='course')

    class Meta:
        model = TermCourse
        fields = '__all__'


class CourseScheduleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseScheduleContent
        fields = '__all__'


class CourseScheduleContentDetailSerializer(serializers.ModelSerializer):
    study_material_info = StudyMaterialListSerializer(read_only=True, source='study_material')

    class Meta:
        model = CourseScheduleContent
        fields = '__all__'


class CourseScheduleStudentSerializer(serializers.ModelSerializer):
    term_course_info = TermCourseSerializer(read_only=True, source='term_course')

    class Meta:
        model = CourseScheduleStudent
        fields = '__all__'


class UserStudyRecordSerializer(serializers.ModelSerializer):
    lesson_info = LessonListSerializer(source='lesson', read_only=True)

    class Meta:
        model = UserStudyRecord
        fields = '__all__'


class LessonDetailSimpleListSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    cards = CardDetailSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
