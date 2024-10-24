from flask import Blueprint
from flask_restful import Api

sku_bp = Blueprint('[sku]', __name__, url_prefix='/api/sku')
# 创建Api对象
sku_api = Api(sku_bp)

from . import views