import string
import os
from db_factory import SpcDBFactory
from config import SpcDBPoolConfig
from flask import Flask, request, make_response, jsonify, Response, json
import ai_service

# 创建一个Flask实例
app = Flask(__name__)
# 在创建 Flask 应用时设置 strict_slashes 参数为 False
#app.url_map.strict_slashes = False

# 2.根据环境变量MY_ENV判断加载不同环境再在不同配置文件
if os.getenv("MY_ENV") == 'DEV':
    app.config.from_pyfile('./config_dev.py')
elif os.getenv("MY_ENV") == 'PROD':
    app.config.from_pyfile('./config_prod.py')
else:
    app.config.from_pyfile('./config_dev.py')

    # 3 初始化相关配置文件
SpcDBPoolConfig.init(app.config)

# 4. 初始化db2连接池资源
SpcDBFactory.init_pool(SpcDBPoolConfig)


@app.route("/")
def index():
    return create_response('{"status":"It works."}')


@app.route("/api/v1/gum-sheeting", methods=['POST'])
def do_something() -> Response:
    row_data = request.data
    try:
        # ai_result = fake_ai_service_run(row_data) # nosonar
        ai_result = ai_service.run(row_data)
        print(ai_result)
        return create_response(ai_result)
    except Exception as e:
        print("Exception: ", e)
        return create_response(jsonify({"code": 500, "ex": str(e)}), status_code=500)


def create_response(result: string, status_code=200) -> Response:
    # 创建响应对象并设置响应体
    response = make_response(result)
    # 设置响应头
    response.headers['Content-Type'] = 'application/json'
    response.status_code = status_code
    return response


def run_ai(raw_data: string) -> dict:
    # 这里写调用 AI 的函数
    # AI 函数的入参是一个字符串
    # AI 函数的返回值是一个 字典
    # ai_service.run(raw_data)
    pass

# 这是个假的 AI 函数
# raw_data = {"time": [2024,7,30,0,0]}
def fake_ai_service_run(raw_data: string) -> dict:
    time_point = json.loads(raw_data)['time']
    # [2024, 7, 30, 0, 0]
    print("time_point = ", time_point)

    # 返回结果
    return {"data": {
        "key1": "value1",
        "key2": "value2"
    }, "status": 200}



def main() -> None:
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    main()
