from rest_framework import serializers

from .models import Course, StudyMaterial, Lesson, Card, Tag, EnumConfig, Survey, Question, UserResponse, \
    CourseScheduleContent
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
    cards = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), many=True)

    class Meta:
        model = Lesson
        fields = '__all__'

    def create(self, validated_data):
        # 提取并移除cards字段，以便稍后手动添加
        cards_data = validated_data.pop('cards', None)
        instance = super().create(validated_data)

        if cards_data:
            # 添加卡片到lesson的多对多关系，并保持请求中传递的顺序
            for index, card in enumerate(cards_data):
                instance.cards.add(card, through_defaults={'order': index})

        return instance

    def update(self, instance, validated_data):
        # 更新实例的字段
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        # 其他字段的更新...

        # 提取并移除cards字段，以便稍后手动添加
        cards_data = validated_data.pop('cards', None)
        instance.save()

        if cards_data:
            # 清除当前关系
            instance.cards.clear()
            # 添加卡片到lesson的多对多关系，并保持请求中传递的顺序
            for index, card in enumerate(cards_data):
                instance.cards.add(card, through_defaults={'order': index})

        return instance

    def get_type_description(self, obj):
        # 调用Course模型中的type_description属性
        return obj.type_description

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_cards = instance.cards.through.objects.filter(lesson=instance).order_by('id')
        ret['cards'] = [i.card_id for i in sorted_cards]
        return ret


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
    study_materials = serializers.PrimaryKeyRelatedField(queryset=StudyMaterial.objects.all(), many=True)

    # study_materials = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = '__all__'

    def create(self, validated_data):
        study_materials_data = validated_data.pop('study_materials', None)
        instance = super().create(validated_data)

        if study_materials_data:
            for index, study_material in enumerate(study_materials_data):
                instance.study_materials.add(study_material, through_defaults={'order': index})

        return instance

    def update(self, instance, validated_data):
        study_materials_data = validated_data.pop('study_materials', None)
        instance = super().update(instance, validated_data)

        if study_materials_data:
            instance.study_materials.clear()
            for index, study_material in enumerate(study_materials_data):
                instance.study_materials.add(study_material, through_defaults={'order': index})

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_study_materials = instance.study_materials.through.objects.filter(card=instance).order_by('id')
        ret['study_materials'] = [i.studymaterial_id for i in sorted_study_materials]
        return ret

    # def get_study_materials(self, obj):
    #     _card_study_materials = CardStudyMaterial.objects.filter(card=obj.id).values_list('studymaterial__id',
    #                                                                                       flat=True).all()
    #     return _card_study_materials

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

    # study_materials = StudyMaterialSimpleListSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sorted_study_materials = instance.study_materials.through.objects.filter(card=instance).order_by('id')
        ret['study_materials'] = [StudyMaterialSimpleListSerializer(i.studymaterial).data for i in
                                  sorted_study_materials]
        return ret


class LessonDetailSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    cards = serializers.PrimaryKeyRelatedField(queryset=Card.objects.all(), many=True)

    class Meta:
        model = Lesson
        fields = '__all__'

    def to_representation(self, instance):
        data = super(LessonDetailSerializer, self).to_representation(instance)
        sorted_cards = instance.cards.through.objects.filter(lesson=instance).order_by('id')  # 按照 Card 表中的 id 排序
        card_data = [CardListSerializer(i.card).data for i in sorted_cards]
        data['cards'] = card_data
        return data


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


class SurveyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        # fields = ['survey', 'user', 'question', 'answer', 'response_time']
        fields = '__all__'

    def create(self, validated_data):
        # 尝试获取唯一的约束
        survey = validated_data.get('survey')
        user = validated_data.get('user')
        question = validated_data.get('question')

        # 检查是否存在具有相同 survey, user, question 的实例
        try:
            existing_response = UserResponse.objects.get(survey=survey, user=user, question=question)
            # 如果存在，则更新现有的实例
            for key, value in validated_data.items():
                setattr(existing_response, key, value)
            existing_response.save()
            return existing_response
        except UserResponse.DoesNotExist:
            # 如果不存在，则创建新的实例
            return super().create(validated_data)


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


class CourseScheduleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseScheduleContent
        fields = '__all__'


class LessonDetailSimpleListSerializer(serializers.ModelSerializer):
    """
    课时序列化
    """
    cards = CardDetailSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
