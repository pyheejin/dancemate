from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager
from datetime import datetime, timedelta

from database.models import *
from database.schema import *
from database.base_model import DefaultModel, DefaultLoginModel
from config.jwt_handler import JWT
from config.constant import *


def get_home(session):
    response = DefaultModel()

    format = '%Y-%m-%d %H:%M:%S'
    today = datetime.strptime(datetime.now().date().strftime(format), format)
    tomorrow = datetime.strptime((datetime.now().date()+timedelta(days=1)).strftime(format), format)

    recommend_users = session.query(User
                            ).outerjoin(RecommendUser, RecommendUser.user_id == User.id
                            ).filter(User.status == constant.STATUS_ACTIVE,
                                     RecommendUser.status == constant.STATUS_ACTIVE).all()
    today_courses = session.query(Course
                            ).outerjoin(CourseDetail,
                                        and_(CourseDetail.course_id == Course.id,
                                             CourseDetail.status == constant.STATUS_ACTIVE)
                            ).outerjoin(UserCourse,
                                        and_(UserCourse.course_detail_id == CourseDetail.id,
                                             UserCourse.status == constant.STATUS_ACTIVE)
                            ).filter(Course.status == constant.STATUS_ACTIVE,
                                     CourseDetail.course_date.between(today, tomorrow)
                            ).options(contains_eager(Course.course_detail),
                            ).all()
    reserve_courses = session.query(Course
                            ).outerjoin(CourseDetail,
                                        and_(CourseDetail.course_id == Course.id,
                                             CourseDetail.status == constant.STATUS_ACTIVE)
                            ).outerjoin(UserCourse,
                                        and_(UserCourse.course_detail_id == CourseDetail.id,
                                             UserCourse.status == constant.STATUS_ACTIVE)
                            ).filter(Course.status == constant.STATUS_ACTIVE,
                                     UserCourse.user_id == 1
                            ).options(contains_eager(Course.course_detail),
                            ).all()

    response.result_data = {
        'recommend_users': user_list_schema.dump(recommend_users),
        'today_courses': course_list_schema.dump(today_courses),
        'reserve_courses': course_list_schema.dump(reserve_courses),
    }
    return response


