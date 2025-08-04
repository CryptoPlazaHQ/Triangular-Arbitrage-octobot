(myenv) PS C:\Users\DELL\Triangular-Arbitrage-octobot> streamlit run dashboard.py

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.4:8501

2025-08-04 17:54:49.748 Uncaught app execution
Traceback (most recent call last):
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 128, in exec_func_with_error_handling
    result = func()
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\myenv\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 669, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Triangular-Arbitrage-octobot\dashboard.py", line 236, in <module>
    st.experimental_rerun()
    ^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'streamlit' has no attribute 'experimental_rerun'. Did you mean: 'experimental_user'?


❌ Error connecting to binanceus: There is no current event loop in thread 'ScriptRunner.scriptThread'.


Also logo is not been displayed are you using right path to call this github hosted as raw content¨?