from flask import Blueprint
from flask_restful import Api
# 创建蓝图对象
recordLog_bp = Blueprint('recordLog', __name__, url_prefix='/api/recordLog')
# 创建Api对象
recordLog_api = Api(recordLog_bp)

# 导入视图
from . import views