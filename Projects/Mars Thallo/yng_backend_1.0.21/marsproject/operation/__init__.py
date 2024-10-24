from flask import Blueprint
from flask_restful import Api

# 创建蓝图对象
operation_bp = Blueprint('operation', __name__,url_prefix='/api/operation')
# 创建Api对象
operation_api = Api(operation_bp)


# 导入视图
from . import views