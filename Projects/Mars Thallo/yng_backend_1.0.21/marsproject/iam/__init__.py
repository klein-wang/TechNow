from flask import Blueprint
from flask_restful import Api
# 创建蓝图对象
user_bp = Blueprint('iam', __name__,url_prefix='/api/iam')
# 创建Api对象
user_api = Api(user_bp)

# 导入视图
from . import views