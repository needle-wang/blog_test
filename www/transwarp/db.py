#!/usr/bin/env python
# encoding: utf-8
#数据库模块 , 实现基本的数据库访问API
#2015年 04月 18日 星期六 12:07:41 CST

import time , uuid , functools , threading , logging

class Dict(dict):
    '''
    支持x.y风格
    '''
    def __init__(self, names = () , values = () , **kw):
        super(Dict , self).__init__(**kw)
        for k , v in zip(names , values):
            self[k] = v

    def __getattr__(self , key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self , key , value):
        self[key] = value

def next_id(t = None):
    if t is None:
        t = time.time()
    return '%015d %s000' % (int(t * 100) , uuid.uuid4().hex)

def _profiling(start , sql = ''):
    t = time.time() - start
    log_mesg = '[profiling] [DB] %s: %s' % (t , sql)
    if t > 0.1:
        logging.warning(log_mesg)
    else:
        logging.warning(log_mesg)

class DBError(Exception):
    pass

class MultiColumnErorr(DBError):
    pass

class _LasyConnection(object):

    def __init__(self):
        '''
        创建本实例时connection属性为None , 用来储存真正的连接对象
        只有在调用cursor()时才会创建数据库连接
        所以叫lasy connection
        '''
        self.connection = None

    def cursor(self):
        if self.connection is None:
            connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(connection)))
            self.connection = connection
        return self.connection.cursor()
    
    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()

class _DbCtx(threading.local):
    '''
    持有数据库连接的上下文对象
    '''

    def __init__(self):
        '''
        本实例的connection属性用来储存_LasyConnection对象
        '''
        self.connection = None
        self.transactions = 0
    
    def is_init(self):
        return self.connection is not None

    def init(self):
        #此时connection才非空 , 是一个_LasyConnection对象
        self.connection = _LasyConnection()
        self.transactions = 0
    
    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()

_db_ctx = _DbCtx()

engine = None

class _Engine(object):
    '''
    数据库引擎对象
    '''

    def __init__(self , connect):
        '''
        _connect储存的是一个lambda函数 , 里面调用了mysql API的连接函数
        '''
        self._connect = connect

    def connect(self):
        return self._connect()

def create_engine(user , passwd , database , **kw):
    import mysql.connector
    global engine
    if engine is not None:
        raise DBError('Engine is already initialized.')
    params = dict(user = user , passwd = passwd , db = database)
    defaults = dict(use_unicode = True , charset = 'utf8' , collation = 'utf8_general_ci' , autocommit = False)
    for k , v in defaults.iteritems():
        params[k] = kw.pop(k , v)
    params.update(kw)
    params['buffered'] = True
    #初始化全局变量engine
    engine = _Engine(lambda:mysql.connector.connect(**params))
    logging.info('Init mysql engine <%s> ok.' % hex(id(engine)))

class _ConnectionCtx(object):
    '''
    数据库连接的上下文 , 目的是自动连接和释放连接
    '''

    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self , exctype , excvalue , traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()

def connection():
    return _ConnectionCtx()

def with_connection(func):
    @functools.wraps(func)
    def _wrapper(*args , **kw):
        with _ConnectionCtx():
            return func(*args , **kw)
    return _wrapper

'''
usage:
with connection():
    do_some_db_operation()
or:
@with_connection
def do_some_db_operation():
    pass
'''

class _TransactionCtx(object):
    def __enter__(self):
        global _db_ctx
        self.should_close_conn = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_conn = True
        _db_ctx.transactions = _db_ctx.transactions + 1
        logging.info('begin transaction...' if _db_ctx.transactions == 1 else 'join current transaction...')
        return self

    def __exit__(self , exctype , excvalue , traceback):
        global _db_ctx
        _db_ctx.transactions = _db_ctx.transactions - 1
        try:
            if _db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        logging.info('commit transaction...')
        try:
            _db_ctx.connection.commit()
            logging.info('commit ok.')
        except:
            logging.warning('commit failed. try rollback...')
            _db_ctx.connection.rollback()
            logging.warning('rollback ok.')
            raise

    def rollback(self):
        global _db_ctx
        logging.warning('rollback transaction...')
        _db_ctx.connection.rollback()
        logging.info('rollback ok.')

def transaction():
    return _TransactionCtx()

def with_transaction(func):
    @functools.wraps(func)
    def _wrapper(*args , **kw):
        _start = time.time()
        with _transactionCtx():
            return func(*args , **kw)
        _profiling(_start)
    return _wrapper

def _select(sql , first ,  * args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?' , '%s')
    logging.info('SQL: %s , ARGS: %s' % (sql , args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql , args)
        if cursor.description:
            names = [x[0] for x in cursor.description]
        if first:
            values = cursor.fetchone()
            if not values:
                return None
            return Dict(names , values)
        return [Dict(names , x) for x in cursor.fetchall()]
    finally:
        if cursor:
            cursor.close()

@with_connection
def select_one(sql , *args):
    return _select(sql , True , *args)

@with_connection
def select_int(sql , *args):
    d = _select(sql , True , *args)
    if len(d) != 1:
        raise MultiColumnErorr('Expect only one column.')
    return d.values()[0]

@with_connection
def select(sql , *args):
    return _select(sql , True , *args)

@with_connection
def _update(sql , *args):
    global _db_ctx
    cursor = None
    sql = sql.replace('?' , '%s')
    logging.info('SQL: %s , ARGS: %s' % (sql , args))
    try:
        cursor = _db_ctx.connection.cursor()
        cursor.execute(sql , args)
        r = cursor.rowcount
        if _db_ctx.transactions == 0:
            logging.info('auto commit.')
            _db_ctx.connection.commit()
        return r
    finally:
        if cursor:
            cursor.close()

def insert(table , **kw):
    cols , args = zip(*kw.iteritems())
    sql = 'insert into `%s`(%s) values(%s)' % (table , ' , '.join(['`%s`' % col for col in cols]) , ','.join(['?' for i in range(len(cols))]))
    return _update(sql , *args)

def update(sql , *args):
    return _update(sql , *args)

def main():
    logging.basicConfig(level = logging.DEBUG)
    create_engine('root' , 'mysqlp@ssword' , 'test')
    update('drop table if exists user')
    update('create table user(id int primary key , name text , email text , passwd text , last_modified real)')
    a = select('show tables;')
    print a

if __name__ == '__main__':
    main()

