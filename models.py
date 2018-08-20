import json

from utils import log


def save(data, path):
    """
    本函数把一个 dict 或者 list 写入文件
    data 是 dict 或者 list
    path 是保存文件的路径
    """    
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        log('save', path, s, data)
        f.write(s)


def load(path):
    """
    本函数从一个文件中载入数据并转化为 dict 或者 list
    path 是保存文件的路径
    """
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        log('load', s)
        return json.loads(s)


class Model(object):   
    @classmethod
    def db_path(cls):
        """
        返回数据的存储路径
        """
        classname = cls.__name__
        path = '{}.txt'.format(classname)
        return path

    @classmethod
    def all(cls):
        """
        得到一个类的所有存储的实例
        """
        path = cls.db_path()
        models = load(path)
        ms = [cls.new(m) for m in models]
        return ms

    @classmethod
    def new(cls, form):
        m = cls(form)
        return m

    @classmethod
    def find_by(cls, **kwargs):
        ms = cls.all()
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        for m in ms:
            if v == m.__dict__[k]:
                return m
        return None

    @classmethod
    def find_all(cls, **kwargs):
        ms = cls.all()
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        data = []
        for m in ms:
            if v == m.__dict__[k]:
                data.append(m)
        return data

    def save(self):
        """
        save 函数用于把一个 Model 的实例保存到文件中
        """
        models = self.all()
        log('models', models)
        if self.__dict__.get('id') is None:
            # 没有 id 就增加一个 id
            if len(models) > 0:
                # 说明不是第一个数据
                self.id = modles[-1].id + 1
            else:
                # 说明是第一个数据
                self.id = 1
            models.append(self)
        else:
            # id 已经存在，就找到并替换
            index = -1
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            # 如果找到，就替换
            if index > -1:
                models[index] = self
        
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    def __repr__(self):
        """
        自定应显示函数
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)


class User(Model):
    def __init__(self, form):
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_login(self):
        users = User.all()
        for u in users:
            if u.username == self.username and u.password == self.password:
                return True
        return False        

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2


# 定义一个 class 用于保存 message
class Message(Model):
    def __init__(self, form):
        self.author = form.get('author', '')
        self.message = form.get('message', '')
