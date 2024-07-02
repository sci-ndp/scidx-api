FROM python:3.9
 
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./api /code/api
COPY ./env_variables /code/env_variables
 
CMD ["fastapi", "run", "api/main.py", "--port", "8000"]