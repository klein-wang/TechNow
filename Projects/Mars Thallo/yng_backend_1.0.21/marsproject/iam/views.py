from marsproject.iam import user_bp, user_api
from flask import request, make_response, jsonify, g
from flask_restful import Resource, reqparse
import re
from marsproject.utils.iam.token import generate_token, login_required, build_menu_tree
from marsproject.utils.iam.user_utils import check_password, generate_password
from .models import *
from marsproject.utils.http_resp_util import Status, Message, http_resp
import traceback
from marsproject.utils.log_util import get_log
from ..recordlog.service import insert_event_data_pre
from ..utils.string_utils import arrToSplInt

logger = get_log(__name__)


# 登录功能
@user_bp.route('/login', methods=['POST'])
def login():
    # 获取用户名
    name = request.get_json().get('name')  # content-type: application/json
    # 获取密码
    pwd = request.get_json().get('pwd')
    logger.debug('user {} login'.format(name))
    # 判断是否传递数据完整
    if not all([name, pwd]):
        return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.PARAMS_LOSS})
    else:
        # 通过用户名获取用户对象
        user = get_user_by_name_or_user_number(str(name).strip())
        # 判断用户是否存在
        if not user:
            logger.debug('no user: {}'.format(name))
            return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_NAME_ERROR})
        # 判断密码是否正确
        if not check_password(pwd, user['pwd']):
            return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_PASSWORD_ERROR})
        user_id = user['id']
        role_list = get_roles_by_user_id(user_id)
        if len(role_list) < 1:
            return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_NO_CONFIG_ROLE})
        menus, buttons = get_permissions_by_user_id(user_id)
        if len(menus) < 1:
            return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_ROLE_NO_CONFIG_PERMISSION})
        menus_tree = build_menu_tree(menus, parent_id=0)
        permissions = {'menus': menus_tree, 'buttons': buttons}
        # 生成一个token
        token = generate_token({'id': user_id, 'user_name': name})
        res = {'code': Status.SUCCESS, 'msg': Message.USER_LOGIN_SUCCESS,
               'data': {'token': token, 'userid': user_id, 'roles': role_list, 'permissions': permissions}}

        return http_resp(res)


class Users(Resource):
    @login_required
    def get(self):
        # 创建RequestParser对象
        parser = reqparse.RequestParser()
        # 添加参数
        parser.add_argument('pnum', type=int, default=1, location='args')
        parser.add_argument('psize', type=int, default=2, location='args')
        parser.add_argument('name', type=str, location='args')
        # 解析参数
        args = parser.parse_args()
        # 获取里面的数据
        name = args.get('name')
        pnum = args.get('pnum')
        psize = args.get('psize')
        # 判断是否传递了name
        if name:
            # 获取用户列表
            total, user_list = get_user_list_with_like(name, pnum, psize)
        else:
            # 获取用户列表
            total, user_list = get_user_list_all(pnum, psize)

        if len(user_list) > 0:
            # 查询用户和角色表
            all_user_roles = get_roles_by_userId(arrToSplInt([item['id'] for item in user_list]))
            dict_user_roles = {}
            for urs in all_user_roles:
                if urs['uid'] in dict_user_roles:
                    dict_user_roles[urs['uid']].append(urs['rid'])
                else:
                    dict_user_roles[urs['uid']] = [urs['rid']]

            for item in user_list:
                item['roles'] = dict_user_roles.get(item['id'], [])
        data = {
            'total': total,
            'pnum': pnum,
            'data': user_list
        }
        res = {'code': Message.SUCCESS, 'msg': Message.SUCCESS, 'data': data}

        return http_resp(res)

    # 创建用户
    @login_required
    def post(self):
        res = {'code': Status.SUCCESS, 'data': None, 'msg': Message.SUCCESS}
        try:
            # 注册用户
            user_name = request.get_json().get('user_name')
            # 初始密码
            # 初始密码 对pwd hash变换
            pwd = generate_password('123456')
            # 接收手机号和邮箱
            name = request.get_json().get('name')
            phone = request.get_json().get('phone')
            email = request.get_json().get('email')
            department = request.get_json().get('department')
            roles = request.get_json().get('roles')
            if not all([user_name, name, email, department, roles]):
                return jsonify({'code': Status.PARAMS_ERROR, 'msg': Message.PARAMS_LOSS, 'data': None})
            if phone and not re.match(r'^1[3456789]\d{9}$', phone):
                return jsonify({'code': Status.PARAMS_ERROR, 'msg': Message.USER_PHONE_ILLEGAL, 'data': None})
            # 判断用户名是否存在
            user = get_user_by_name(user_name)
            if user:
                return jsonify({'code': Status.DATA_ERROR, 'data': None, 'msg': Message.USER_EXISTE})
            # 创建用户对象
            # 判断是否传递了角色ID
            user_id = create_user(user_name, name, pwd, email, department, phone)
            # 绑定角色和用户
            create_user_role(user_id, roles)

            # 记录日志
            insert_event_data_pre(type=6, type_name="用户数据修改", content=f"创建用户(id={user_id}, name={name})", operator_user=g.user)

        except Exception as e:
            res['code'] = Status.EXCEPTION_ERROR
            res['msg'] = str(e)
            logger.error("user post method failed detail: {}".format(str(e)))
            logger.error("user post method failed detail: {}".format(traceback.format_exc()))

        return http_resp(res)


user_api.add_resource(Users, '/users/')


class User(Resource):
    @login_required
    def get(self, id):
        user = get_user_by_id(id)
        if user:
            all_role = get_roles_by_single_userId(id)
            user['roles'] = [r['rid'] for r in all_role]
            return jsonify({'status': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': user})
        else:
            return jsonify({'status': Status.DATA_ERROR, 'msg': Message.USER_NO_EXISTE, 'data': None})

    # 修改用户
    @login_required
    def put(self, id):
        """name,pwd,phone,email,user_no,department"""
        try:
            user_name = request.get_json().get('user_name')
            name = request.get_json().get('name')
            phone = request.get_json().get('phone')
            email = request.get_json().get('email')
            department = request.get_json().get('department')
            roles = request.get_json().get('roles')
            if not all([user_name, name, email, department, roles]):
                return jsonify({'code': Status.PARAMS_ERROR, 'msg': Message.PARAMS_LOSS, 'data': None})
            if phone and not re.match(r'^1[3456789]\d{9}$', phone):
                return jsonify({'code': Status.PARAMS_ERROR, 'msg': Message.USER_PHONE_ILLEGAL, 'data': None})

            # 判断用户名除了当前id是否存在
            user_count = get_user_count_by_name(user_name, id)
            if user_count > 0:
                return jsonify({'code': Status.DATA_ERROR, 'data': None, 'msg': Message.USER_EXISTE})

            user = {
                "id": id,
                "user_name": request.get_json().get('user_name'),
                "name": request.get_json().get('name'),
                "phone": request.get_json().get('phone'),
                "email": request.get_json().get('email'),
                "department": request.get_json().get('department'),
                "roles": roles
            }
            # 更新用户
            update_user_by_id(id, user)
            # 获取变更后的角色
            # 删除用户原有角色关联关系
            delete_user_roles_by_uid(id)
            # 创建用户新的角色关联关系
            create_user_role(id, roles)

            # 记录日志
            insert_event_data_pre(type=6, type_name="用户数据修改", content=f"修改用户(id={id}, name={user_name})", operator_user=g.user)

            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': user})
        except Exception as e:
            logger.error("user put method failed detail: {}".format(str(e)))
            logger.error("user put method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})

    @login_required
    def post(self, id):
        try:
            user = get_user_pwd_by_id(id)
            raw_pwd = request.get_json().get('rawPwd')
            new_pwd = request.get_json().get('newPwd')
            # 验证数据的合法性
            if not all([raw_pwd, new_pwd]):
                return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.PARAMS_LOSS})
            # 判断两次密码是否一致
            if raw_pwd == new_pwd:
                return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_OLD_EQUAL_NEW_PASSWORD})
            if not check_password(raw_pwd, user['pwd']):
                return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.USER_OLD_PASSWORD_ERROR})
            new_pwd = generate_password(new_pwd)
            update_user_pwd_by_id(id, new_pwd)

            # 记录日志
            insert_event_data_pre(type=6, type_name="用户数据修改", content=f"修改密码", operator_user=g.user)

            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
        except Exception as e:
            logger.error("user post method failed detail: {}".format(str(e)))
            logger.error("user post method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})

    # 删除用户
    @login_required
    def delete(self, id):
        try:
            user = get_user_by_id(id)
            if user:
                delete_user_by_id(id)
                delete_user_roles_by_uid(id)
                # 记录日志
                insert_event_data_pre(type=6, type_name="用户数据修改", content=f"删除用户(id={id}, name={user['user_name']})",operator_user=g.user)
            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
        except Exception as e:
            logger.error("user delete method failed detail: {}".format(str(e)))
            logger.error("user delete method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})


user_api.add_resource(User, '/user/<int:id>/')


class Roles(Resource):

    @login_required
    def get(self):
        '''
        获取角色列表
        '''
        try:
            roles = get_roles_list_all()
            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': roles})
        except Exception as e:
            logger.error("Roles get method failed detail: {}".format(str(e)))
            logger.error("Roles get method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data':None})

    @login_required
    def put(self):
        '''
              修改角色
              '''
        try:
            role_id = request.get_json().get('id')  # appliction/json
            # 获取传递的名称
            role_name = request.get_json().get('role_name')
            # 获取传递的描述
            info = request.get_json().get('info')
            # 获取权限ids
            permissions = request.get_json().get('permissions')
            # 验证数据的合法性
            if not all([role_id, role_name, info, permissions]):
                return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.PARAMS_LOSS})
            # 判断用户名是否存在
            role = get_role_count_by_name(role_name, role_id)
            if role > 0:
                return jsonify({'code': Status.DATA_ERROR, 'data': None, 'msg': Message.ROLE_EXISTE})
            # 更新role信息
            update_role_by_id(role_id, role_name, info)
            # 删除角色和权限关联关系
            delete_role_premission_by_rid(role_id)
            # 重新绑定角色权限
            create_role_premission(role_id, permissions)
            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
        except Exception as e:
            logger.error("Roles post method failed detail: {}".format(str(e)))
            logger.error("Roles post method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})

    @login_required
    def post(self):
        '''
             添加角色
             '''
        try:
            # 获取传递的名称
            role_name = request.get_json().get('role_name')  # appliction/json
            # 获取传递的描述
            info = request.get_json().get('info')
            # 获取权限ids
            permissions = request.get_json().get('permissions')
            # 验证数据的合法性
            if not all([role_name, info, permissions]):
                return jsonify({'code': Status.PARAMS_ERROR, 'data': None, 'msg': Message.PARAMS_LOSS})
                # 判断用户名是否存在
            role = get_role_by_name(role_name)
            if role:
                return jsonify({'code': Status.DATA_ERROR, 'data': None, 'msg': Message.ROLE_EXISTE})
            # 添加到数据库
            role_id = create_role_ext(role_name, info)
            # 重新绑定角色权限
            create_role_premission(role_id, permissions)
            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
        except Exception as e:
            logger.error("Roles post method failed detail: {}".format(str(e)))
            logger.error("Roles post method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})

    @login_required
    def delete(self):
        try:
            role_id = request.get_json().get('id')
            role_d = get_single_role_by_id(role_id)
            if role_d:
                delete_user_roles_by_rid(role_id)
                delete_role_premission_by_rid(role_id)
                delete_roles_by_id(role_id)
            return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
        except Exception as e:
            logger.error("user delete method failed detail: {}".format(str(e)))
            logger.error("user delete method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})


user_api.add_resource(Roles, '/roles/')


class Permissions(Resource):
    @login_required
    def get(self):
        # 获取前端页面要求的数据类型,list tree
        type_ = request.args.get('type_')
        try:
            # 根据type_决定以什么结构返回数据
            if type_ == 'tree':
                # 通过模型获取数据
                menu_list = get_permission_list_all()
                menu_data = build_menu_tree(menu_list,parent_id=0)
                return jsonify({'code':Status.SUCCESS,'msg': Message.SUCCESS,'data':menu_data})
            else:
                # 通过模型获取数据
                menu_list = get_permission_list_all()
                return jsonify({'code':Status.SUCCESS,'msg':Message.SUCCESS,'data':menu_list})
        except Exception as e:
            logger.error("Permissions get method failed detail: {}".format(str(e)))
            logger.error("Permissions get method failed detail: {}".format(traceback.format_exc()))
            return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})


user_api.add_resource(Permissions,'/permissions/')


@user_bp.route('/reset_pwd/<int:id>/')
@login_required
def rest_pwd(id):
    try:
        # 初始密码
        init_pwd = '123456'
        # 初始密码hash
        pwd = generate_password(init_pwd)
        init_password_by_id(id, pwd)
        return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
    except Exception as e:
        logger.error("rest_pwd failed detail: {}".format(str(e)))
        logger.error("rest_pwd failed detail: {}".format(traceback.format_exc()))
        return jsonify({'code': Status.EXCEPTION_ERROR, 'msg': Message.ERROR, 'data': None})


@user_bp.route('/test/')
@login_required
def test_login_required():
    return jsonify({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None})
