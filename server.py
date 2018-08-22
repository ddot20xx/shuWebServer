# coding: utf-8

import socket
import urllib.parse
import _thread

from utils import (
    log,
    error,
)

from routes.routes_static import route_static
from routes.routes_user import route_dict as user_routes
from routes.todo import route_dict as todo_routes
from routes.api_todo import route_dict as api_todo


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f

    def add_cookies(self):
        cookies = self.headers.get('cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        self.headers = {}
        for line in header:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # set cookies
        self.cookies = {}
        self.add_cookies()
        
     def json(self):
        """
        把 body 中的 json 格式字符串解析成 dict 或者 list 并返回
        """
        import json
        return json.loads(self.body)



request = Request()


def parsed_path(path):
    """
    将 path 解析为 path 和 query
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    """
    根据 path 调用相应的 route 处理函数
    没有处理的 path 会返回 404
    """
    r = {
        '/static': route_static,        
    }
    r.update(api_todo)
    r.update(user_routes)
    r.update(todo_routes)
    response = r.get(path, error)
    return response(request)


def process_request(connection):
    r = connection.recv(1024)
    r = r.decode('utf-8')
    log('完整请求')
    log('请求结束')  
    # 因为 chrome 会发送空请求导致 split 得到空 list
    # 所以这里判断一下防止程序崩溃
    if len(r.split()) < 2:
        connection.close()
    path = r.split()[1]
    # 创建一个新的 request 并设置
    request = Request()
    request.method = r.split()[0]
    request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
    # 把 body 放入 request 中
    request.body = r.split('\r\n\r\n', 1)[1]
    # 用 response_for_path 函数来得到 path 对应的响应内容
    response = response_for_path(path, request)
    # 把响应发送给客户端
    connection.sendall(response)
    # print('完整响应')
    try:
        log('响应\n', response.decode('utf-8').replace('\r\n', '\n'))
    except Exception as e:
        log('异常', e)
    # 处理完请求, 关闭连接
    connection.close()
    # print('关闭')

    
def run(host='', port=3000):
    """
    启动服务器
    """
    # 初始化 socket  
    print('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 监听 接受 读取请求数据 解码成字符串
        s.listen(3)
        # 无限循环来处理请求
        while True:
            connection, address = s.accept()
            print('连接成功, 使用多线程处理请求', address)
            # 开一个新的线程来处理请求
            _thread.start_new_thread(process_request, (connection,))


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )
    run(**config)
