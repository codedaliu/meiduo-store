"""
任务就是普通的函数
1 这个普通的函数必须要被celery实例对象的task装饰器装饰
2 这个任务需要celery自己去检测

"""
#
# from xadmin.plugins import mobile
# from clery_tasks.main import app
# from libs.yuntongxun.sms import CCP
#
# @app.task
# def send_sms_code(sms_code=None):
#     CCP().send_template_sms(mobile, [sms_code, 5], 1)

#########################################################

from libs.yuntongxun.sms import CCP
from clery_tasks.main import app

@app.task
def send_sms_code(mobile,sms_code):

    CCP().send_template_sms(mobile, [sms_code, 5], 1)