from datetime import datetime, timedelta

from django.test import TestCase
from apps.ftz.models import TermCourse, ExternalUser, Course
from .services import TermCourseService


class TermCourseServiceTest(TestCase):
    def setUp(self):
        self.user = 1
        self.course = 2
        # 创建测试数据和模型实例
        # self.course = Course.objects.create(title="Test Course", description="A course for testing")
        # self.user = ExternalUser.objects.create(username="testuser")
        # self.term_course = TermCourse.objects.create(
        #     course=self.course,
        #     term_number=1,
        #     term_type="test",
        #     version="1.0",
        #     total_days=30,
        #     enrollment_start=datetime.now(),
        #     enrollment_end=datetime.now() + timedelta(days=30),
        #     course_start=datetime.now() + timedelta(days=5),
        #     course_end=datetime.now() + timedelta(days=35),
        #     teacher="Test Teacher",
        #     teacher_qr_code="teacher_qr_code",
        #     assistant_teacher="Test Assistant",
        #     assistant_teacher_qr_code="assistant_qr_code"
        # )
        pass

    def test_get_only_term(self):
        # 测试获取正在售卖的期课
        service = TermCourseService(self.user, self.course)
        current_term = service.get_only_term()
        self.assertIsNotNone(current_term)
        self.assertEqual(current_term.term_number, 1)

    # 您可以在这里添加更多的测试方法来测试其他功能


# 运行测试
if __name__ == '__main__':
    import unittest

    unittest.main()
