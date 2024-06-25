from apps.ftz.models import CourseScheduleStudent, TermCourse
from apps.ftz.serializers import CourseScheduleStudentSerializer
from apps.mall.models import Order, Product
from apps.mall.serializers import OrderDetailSerializer
from apps.user_center.models import ExternalUser
from apps.user_center.serializers import ExternalUserSerializer


class UserCourseService:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = self._query_user()

    def _query_user(self):
        user = ExternalUser.objects.filter(id=self.user_id).order_by('-id').first()
        return user

    def query_term(self):
        return CourseScheduleStudent.objects.filter(user=self.user_id).all()

    def query_product_order(self):
        return Order.objects.filter(user=self.user_id).all()

    def query_all_info(self):
        user_info = ExternalUserSerializer(self.user).data
        term_info = CourseScheduleStudentSerializer(self.query_term(), many=True).data
        product_order_info = OrderDetailSerializer(self.query_product_order(), many=True).data
        return {
            'user_info': user_info,
            'course_schedule_student_info': term_info,
            'product_order_info': product_order_info
        }

    def reset_course_info(self, term_id):
        '''
        1. 查询期课订单
        2. 删除订单支付记录
        3. 删除订单
        4. 从期课学员表删除
        '''

        term_obj = TermCourse.objects.filter(id=term_id).get()
        if not term_obj:
            return
        product_obj = Product.objects.filter(course_id=term_obj.course_id).get()
        if not product_obj:
            return
        order_obj = Order.objects.filter(product=product_obj.id, user=self.user_id).get()
        if order_obj:
            # 删除订单和订单记录
            pass
        course_schedule_student_obj = CourseScheduleStudent.objects.filter(term_course=term_id, user=self.user_id).get()
        if course_schedule_student_obj:
            #
            pass
        return


