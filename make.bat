@echo off

if "%1"=="cov" goto coverage
if "%1"=="prec" goto pre_commit
if "%1"=="run" goto run

echo Unknown command: %1
goto end

:coverage
:: test coverage check with html report
coverage run -m pytest
coverage report
coverage html
goto end

:pre_commit
:: run pre-commit checks manually
pre-commit run --all-files
goto end

:run
:: run the streamlit app
streamlit run streamlit_app.py
goto end

:end
