
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://10.5.0.2:8501

2025-08-07 18:31:31.878 Uncaught app execution
Traceback (most recent call last):
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1961, in _exec_single_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, str_statement, effective_parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\default.py", line 944, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
psycopg2.OperationalError: server closed the connection unexpectedly
        This probably means the server terminated abnormally
        before or while processing the request.
server closed the connection unexpectedly
        This probably means the server terminated abnormally
        before or while processing the request.


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 128, in exec_func_with_error_handling
    result = func()
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 669, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\dashboard.py", line 18, in <module>
    database.init_db()
    ~~~~~~~~~~~~~~~~^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\triangular_arbitrage\database.py", line 16, in init_db
    conn.execute(text("""
    ~~~~~~~~~~~~^^^^^^^^^
    CREATE TABLE IF NOT EXISTS arbitrage_runs (
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
    );
    ^^
    """))
    ^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1413, in execute
    return meth(
        self,
        distilled_parameters,
        execution_options or NO_OPTIONS,
    )
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\sql\elements.py", line 526, in _execute_on_connection       
    return connection._execute_clauseelement(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        self, distilled_params, execution_options
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1635, in _execute_clauseelement       
    ret = self._execute_context(
        dialect,
    ...<8 lines>...
        cache_hit=cache_hit,
    )
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1840, in _execute_context
    return self._exec_single_context(
           ~~~~~~~~~~~~~~~~~~~~~~~~~^
        dialect, context, statement, parameters
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1980, in _exec_single_context
    self._handle_dbapi_exception(
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        e, str_statement, effective_parameters, cursor, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 2349, in _handle_dbapi_exception      
    raise sqlalchemy_exception.with_traceback(exc_info[2]) from e
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\base.py", line 1961, in _exec_single_context
    self.dialect.do_execute(
    ~~~~~~~~~~~~~~~~~~~~~~~^
        cursor, str_statement, effective_parameters, context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\sqlalchemy\engine\default.py", line 944, in do_execute
    cursor.execute(statement, parameters)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) server closed the connection unexpectedly
        This probably means the server terminated abnormally
        before or while processing the request.
server closed the connection unexpectedly
        This probably means the server terminated abnormally
        before or while processing the request.

[SQL:
        CREATE TABLE IF NOT EXISTS arbitrage_runs (
            id SERIAL PRIMARY KEY,
            exchange VARCHAR(255) NOT NULL,
            profit_percentage DOUBLE PRECISION NOT NULL,
            timestamp TIMESTAMP NOT NULL
        );
        ]
(Background on this error at: https://sqlalche.me/e/20/e3q8)
