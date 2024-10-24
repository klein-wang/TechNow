from flask import jsonify, make_response


class Status:

    SUCCESS = 200
    # 参数错误
    PARAMS_ERROR = 301
    # 数据相关的错误
    DATA_ERROR = 302
    # 系统级别错误预留
    SYSTEM_ERROR = 400
    # 业务异常错误
    EXCEPTION_ERROR = 401


class Message:

    SUCCESS = "success !"
    ERROR = "error "
    PARAMS_LOSS = "请求参数不全 ..."
    NO_RESP_AML_DATA = "AML推荐数据为空!"
    VALUE_LIMIT_ERROR = "回写值超出上下限范围!"
    VALUE_ERROR = "值错误"
    OPERATOR_ERROR = "已有操作在进行, 请稍后重试!"
    NO_REPEAT_OPERATOR = "状态已改变, 请不重复操作!"
    VALUE_NO_CHANGE = "操作失败, 没有修改任何值!"
    VALUE_NOT_NULL = "值不可为空!"
    USER_NAME_ERROR = "用户名错误"
    USER_PASSWORD_ERROR = "密码错误"
    USER_NO_CONFIG_ROLE = "当前用户未配置角色"
    USER_ROLE_NO_CONFIG_PERMISSION = "当前用户对应的角色未配置菜单权限"
    USER_LOGIN_SUCCESS = "登录成功"
    USER_NO_EXISTE = "用户不存在"
    USER_ILLEGAL = "用户名不合法"
    USER_PHONE_ILLEGAL = "手机号不合法"
    USER_EXISTE = "用户名已存在"
    USER_OLD_EQUAL_NEW_PASSWORD = "新旧密码不能相同"
    USER_OLD_PASSWORD_ERROR = "原始密码输入错误"
    USER_RESET_PASSWORD_SUCCESS = "重置密码成功,密码为123456"
    USER_NUMBER_ERROR = "工号不可为空"
    USER_NUMBER_EXISTE = "工号已存在"
    SKU_REPEAT_DATA = "sku不可重复!"
    OPERATOR_REPEAT_ERROR = "已有修改操作在进行,请稍后重试!"
    SKU_NAME_NOT_NULL = "sku不可为空!"
    ROLE_EXISTE = "角色已存在"
    SKU_NAME_IS_NULL = "当前sku值为空,无法获取上下限数据!"
    SKU_NAME_IS_NOT_CONFIG = "模型参数中未找到当前sku,无法获取上下限数据!"
    SKU_PARAM_CONFIG_FULL = "模型参数中sku的上下限数据配置不全!"
    SYS_NO_START_TEXT1 = "当前处于停机状态,无法进行模型推荐"
    WRITE_BACK_TAG_FAULT = "操作失败,回写点位存在故障!"
    SKU_NAME_ILLEGAL = "sku名字不合法,必须是[3-4]位字母!"


# 通用的返回参数设置
def http_resp(res):
    # 创建响应对象并设置响应体
    response = make_response(jsonify(res))
    # 设置响应头
    response.headers['Content-Type'] = 'application/json'
    return response
