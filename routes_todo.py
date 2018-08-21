from utils import log
from todo import Todo
from models import User
from routes import current_user


def template(name):
    """
    根据名字读取 templates 文件夹里的一个文件并返回
    """
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def response_with_headers(headers, code=200):
    """
    返回响应的头部    
    """
    header = 'HTTP/1.1 {} VERY OK\r\n'.format(code)
    header += ''.join(['{}: {}\r\n'.format(k, v)
                           for k, v in headers.items()])
    return header


def redirect(url):
    """
    返回重定向的响应。
    body 为空。
    """
    headers = {
        'Location': url,
    }   
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode('utf-8')


def index(request):
    """
    todo 首页的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    # 找到当前登录的用户，如果没登录就重定向到登录页面
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    # todo_list = Todo.all()
    todo_list = Todo.find_all(user_id=u.id)   
    todos = []
    for t in todo_list:
        edit_link = '<a href="/todo/edit?id={}">编辑</a>'.format(t.id)
        delete_link = '<a href="/todo/delete?id={}">删除</a>'.format(t.id)
        s = '<h3>{} : {} {} {}</h3>'.format(t.id, t.title, edit_link, delete_link)
        todos.append(s)
    todo_html = ''.join(todos)
    # 替换模板文件中的标记字符串
    body = template('todo_index.html')
    body = body.replace('{{todos}}', todo_html)   
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def add(request):
    """
    用于增加新 todo 的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    uname = current_user(request)
    u = User.find_by(username=uname)    
    if request.method == 'POST':
        form = request.form()
        t = Todo.new(form)
        t.user_id = u.id
        t.save()   
    return redirect('/todo')


def edit(request):
    """
    用于编辑新 todo 的路由函数
    """
    headers = {
        'Content-Type': 'text/html',
    }
    # 根据 todo_id 得到当前编辑的 todo
    todo_id = int(request.query.get('id', -1))
    t = Todo.find_by(id=todo_id)
    # edit 防护
    uname = current_user(request)
    u = User.find_by(username=uname)
    if t.user_id != u.id:
        return redirect('/login')
    # 替换模板
    body = template('todo_edit.html')
    body = body.replace('{{todo_id}}',str(t.id))
    body = body.replace('{{todo_title}}', str(t.title))
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def update(request):
    """
    用于更新 todo 的路由函数
    """
    if request.method == 'POST':
        form = request.form()
        todo_id = int(form.get('id', -1))
        t = Todo.find_by(id=todo_id)
        t.title = form.get('title', t.title)
        t.save()    
    return redirect('/todo')


def delete_todo(request):
    """
    用于删除 todo 的路由函数
    """
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    todo_id = int(request.query.get('id', -1))
    t = Todo.find_by(id=todo_id)
    if t.user_id != u.id:
        return redirect('/login')
    if t is not None:
        t.remove()
    return redirect('/todo')


def login_required(route_function):
    def f(request):
        uname = current_user(request)
        u = User.find_by(username=uname)
        if u is None:
            return redirect('/login')
        return route_function(request)
    return f


route_dict = {
    '/todo': index,
    '/todo/add': login_required(add),
    '/todo/edit': edit,
    '/todo/update': update,
    '/todo/delete': delete_todo,
}
