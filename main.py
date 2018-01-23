from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'windroc-nwpc-project'

socketio = SocketIO(app)


@app.route('/')
def get_index_page():
    return render_template('base.html')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('my event', namespace='/test')
def test_message(message):
    print(message)
    emit('my response', {'data': message['data'], 'count': 2})


if __name__ == "__main__":
    socketio.run(app)

vepointClause', 'RollbackToSavepointClause', 'SavepointClause', 'ScalarSelect', 'Select', 'SelectBase', 'Selectable', 'TableClause
', 'TableSample', 'TextAsFrom', 'TextClause', 'True_', 'Tuple', 'TypeClause', 'TypeCoerce', 'UnaryExpression', 'Update', 'UpdateBa
se', 'ValuesBase', 'Visitable', 'WithinGroup', '_BinaryExpression', '_BindParamClause', '_Case', '_Cast', '_Executable', '_Exists'
, '_Extract', '_False', '_FromGrouping', '_Generative', '_Grouping', '_Label', '_Null', '_Over', '_ScalarSelect', '_SelectBase', '
_TextClause', '_True', '_Tuple', '_TypeClause', '_UnaryExpression', '__all__', '__builtins__', '__cached__', '__doc__', '__file__'
, '__loader__', '__name__', '__package__', '__spec__', '_clause_element_as_expr', '_clone', '_cloned_difference', '_cloned_interse
ction', '_column_as_key', '_corresponding_column_or_error', '_expression_literal_as_text', '_from_objects', '_interpret_as_from',
'_is_column', '_labeled', '_literal_as_binds', '_literal_as_label_reference', '_literal_as_text', '_only_column_elements', '_selec
t_iterables', '_string_or_unprintable', '_truncated_label', 'alias', 'all_', 'and_', 'any_', 'asc', 'between', 'bindparam', 'case'
, 'cast', 'collate', 'column', 'delete', 'desc', 'distinct', 'except_', 'except_all', 'exists', 'extract', 'false', 'func', 'funcf
ilter', 'insert', 'intersect', 'intersect_all', 'join', 'label', 'lateral', 'literal', 'literal_column', 'modifier', 'not_', 'null
', 'nullsfirst', 'nullslast', 'or_', 'outerjoin', 'outparam', 'over', 'public_factory', 'quoted_name', 'select', 'subquery', 'tabl
e', 'tablesample', 'text', 'true', 'tuple_', 'type_coerce', 'union', 'union_all', 'update', 'within_group']
2018-01-23 22:37:18,059 INFO sqlalchemy.engine.base.Engine SELECT post.id AS post_id, post.title AS post_title, post.content AS po
st_content, post.publish_date AS post_publish_date, post.body_html AS post_body_html, post.user_id AS post_user_id
FROM post
WHERE null
2018-01-23 22:37:18,060 INFO sqlalchemy.engine.base.Engine {}
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?search=%E8%B7%B3%E8%88%9E HTTP/1.1" 500 -
Traceback (most recent call last):
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1997, in __call__
    return self.wsgi_app(environ, start_response)
  File "D:\MyDownloads\flask\lib\site-packages\flask_socketio\__init__.py", line 42, in __call__
    start_response)
  File "D:\MyDownloads\flask\lib\site-packages\engineio\middleware.py", line 49, in __call__
    return self.wsgi_app(environ, start_response)
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1985, in wsgi_app
    response = self.handle_exception(e)
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1540, in handle_exception
    reraise(exc_type, exc_value, tb)
  File "D:\MyDownloads\flask\lib\site-packages\flask\_compat.py", line 33, in reraise
    raise value
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1982, in wsgi_app
    response = self.full_dispatch_request()
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1614, in full_dispatch_request
    rv = self.handle_user_exception(e)
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1517, in handle_user_exception
    reraise(exc_type, exc_value, tb)
  File "D:\MyDownloads\flask\lib\site-packages\flask\_compat.py", line 33, in reraise
    raise value
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1612, in full_dispatch_request
    rv = self.dispatch_request()
  File "D:\MyDownloads\flask\lib\site-packages\flask\app.py", line 1598, in dispatch_request
    return self.view_functions[rule.endpoint](**req.view_args)
  File "D:\MyDownloads\test\flask\app\main\views.py", line 338, in search
    posts=Post.query.filter(Post.title.contains_([keyword]))
  File "D:\MyDownloads\flask\lib\site-packages\sqlalchemy\orm\attributes.py", line 198, in __getattr__
    key)
AttributeError: Neither 'InstrumentedAttribute' object nor 'Comparator' object associated with Post.title has an attribute 'contai
ns_'
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=style.css HTTP/1.1" 200 -
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=jquery.js HTTP/1.1" 200 -
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=debugger.js HTTP/1.1" 200 -
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=ubuntu.ttf HTTP/1.1" 200 -
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=console.png HTTP/1.1" 200 -
127.0.0.1 - - [23/Jan/2018 22:37:18] "GET /search?__debugger__=yes&cmd=resource&f=console.png HTTP/1.1" 200 -
 * Detected change in 'D:\\MyDownloads\\test\\flask\\app\\main\\views.py', reloading
 * Restarting with stat
WebSocket transport not available. Install eventlet or gevent and gevent-websocket for improved performance.
 * Debugger is active!
 * Debugger PIN: 293-805-898
 * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
2018-01-23 22:37:54,684 INFO sqlalchemy.engine.base.Engine SHOW VARIABLES LIKE 'sql_mode'
2018-01-23 22:37:54,684 INFO sqlalchemy.engine.base.Engine {}
D:\MyDownloads\flask\lib\site-packages\pymysql\cursors.py:165: Warning: (1366, "Incorrect string value: '\\xD6\\xD0\\xB9\\xFA\\xB1
\\xEA...' for column 'VARIABLE_VALUE' at row 480")
  result = self._query(query)
2018-01-23 22:37:54,695 INFO sqlalchemy.engine.base.Engine SELECT DATABASE()
2018-01-23 22:37:54,696 INFO sqlalchemy.engine.base.Engine {}
2018-01-23 22:37:54,697 INFO sqlalchemy.engine.base.Engine show collation where `Charset` = 'utf8' and `Collation` = 'utf8_bin'
2018-01-23 22:37:54,698 INFO sqlalchemy.engine.base.Engine {}
2018-01-23 22:37:54,700 INFO sqlalchemy.engine.base.Engine SELECT CAST('test plain returns' AS CHAR(60)) AS anon_1
2018-01-23 22:37:54,700 INFO sqlalchemy.engine.base.Engine {}
2018-01-23 22:37:54,701 INFO sqlalchemy.engine.base.Engine SELECT CAST('test unicode returns' AS CHAR(60)) AS anon_1
2018-01-23 22:37:54,702 INFO sqlalchemy.engine.base.Engine {}
2018-01-23 22:37:54,703 INFO sqlalchemy.engine.base.Engine SELECT CAST('test collated returns' AS CHAR CHARACTER SET utf8) COLLATE
 utf8_bin AS anon_1
2018-01-23 22:37:54,703 INFO sqlalchemy.engine.base.Engine {}
2018-01-23 22:37:54,705 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2018-01-23 22:37:54,706 INFO sqlalchemy.engine.base.Engine SELECT user.id AS user_id, user.email AS user_email, user.username AS u
ser_username, user.password_hash AS user_password_hash, user.confirmed AS user_confirmed, user.name AS user_name, user.location AS
 user_location, user.about_me AS user_about_me, user.merber_since AS user_merber_since, user.last_seen AS user_last_seen, user.ava
tar_hash AS user_avatar_hash, user.role_id AS user_role_id
FROM user
WHERE user.id = %(param_1)s
2018-01-23 22:37:54,707 INFO sqlalchemy.engine.base.Engine {'param_1': 6}
2018-01-23 22:37:54,711 INFO sqlalchemy.engine.base.Engine UPDATE user SET last_seen=%(last_seen)s WHERE user.id = %(user_id)s
2018-01-23 22:37:54,711 INFO sqlalchemy.engine.base.Engine {'last_seen': datetime.datetime(2018, 1, 23, 14, 37, 54, 709785), 'user
_id': 6}
2018-01-23 22:37:54,713 INFO sqlalchemy.engine.base.Engine COMMIT
2018-01-23 22:37:54,777 INFO sqlalchemy.engine.base.Engine BEGIN (implicit)
2018-01-23 22:37:54,779 INFO sqlalchemy.engine.base.Engine SELECT user.id AS user_id, user.email AS user_email, user.username AS u
ser_username, user.password_hash AS user_password_hash, user.confirmed AS user_confirmed, user.name AS user_name, user.location AS
 user_location, user.about_me AS user_about_me, user.merber_since AS user_merber_since, user.last_seen AS user_last_seen, user.ava
tar_hash AS user_avatar_hash, user.role_id AS user_role_id
FROM user
WHERE user.id = %(param_1)s
2018-01-23 22:37:54,780 INFO sqlalchemy.engine.base.Engine {'param_1': 6}
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
['Alias', 'BinaryExpression', 'BindParameter', 'BooleanClauseList', 'CTE', 'Case', 'Cast', 'ClauseElement', 'ClauseList', 'Collect
ionAggregate', 'ColumnClause', 'ColumnCollection', 'ColumnElement', 'CompoundSelect', 'Delete', 'Executable', 'Exists', 'Extract',
 'False_', 'FromClause', 'FromGrouping', 'Function', 'FunctionElement', 'FunctionFilter', 'Generative', 'GenerativeSelect', 'Group
ing', 'HasCTE', 'HasPrefixes', 'HasSuffixes', 'Insert', 'Join', 'Label', 'Lateral', 'Null', 'Over', 'PARSE_AUTOCOMMIT', 'ReleaseSa
vepointClause', 'RollbackToSavepointClause', 'SavepointClause', 'ScalarSelect', 'Select', 'SelectBase', 'Selectable', 'TableClause
', 'TableSample', 'TextAsFrom', 'TextClause', 'True_', 'Tuple', 'TypeClause', 'TypeCoerce', 'UnaryExpression', 'Update', 'UpdateBa
se', 'ValuesBase', 'Visitable', 'WithinGroup', '_BinaryExpression', '_BindParamClause', '_Case', '_Cast', '_Executable', '_Exists'
, '_Extract', '_False', '_FromGrouping', '_Generative', '_Grouping', '_Label', '_Null', '_Over', '_ScalarSelect', '_SelectBase', '
_TextClause', '_True', '_Tuple', '_TypeClause', '_UnaryExpression', '__all__', '__builtins__', '__cached__', '__doc__', '__file__'
, '__loader__', '__name__', '__package__', '__spec__', '_clause_element_as_expr', '_clone', '_cloned_difference', '_cloned_interse
ction', '_column_as_key', '_corresponding_column_or_error', '_expression_literal_as_text', '_from_objects', '_interpret_as_from',
'_is_column', '_labeled', '_literal_as_binds', '_literal_as_label_reference', '_literal_as_text', '_only_column_elements', '_selec
t_iterables', '_string_or_unprintable', '_truncated_label', 'alias', 'all_', 'and_', 'any_', 'asc', 'between', 'bindparam', 'case'
, 'cast', 'collate', 'column', 'delete', 'desc', 'distinct', 'except_', 'except_all', 'exists', 'extract', 'false', 'func', 'funcf
ilter', 'insert', 'intersect', 'intersect_all', 'join', 'label', 'lateral', 'literal', 'literal_column', 'modifier', 'not_', 'null
', 'nullsfirst', 'nullslast', 'or_', 'outerjoin', 'outparam', 'over', 'public_factory', 'quoted_name', 'select', 'subquery', 'tabl
e', 'tablesample', 'text', 'true', 'tuple_', 'type_coerce', 'union', 'union_all', 'update', 'within_group']
