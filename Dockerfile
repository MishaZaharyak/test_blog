FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN chmod -R a+rwx /code/media && chmod -R a+rwx /code/redis

#FROM python:3
#ENV PYTHONUNBUFFERED 1
#RUN mkdir /code
#WORKDIR /code
#RUN pip install "poetry==0.12"
#COPY poetry.lock pyproject.toml /code/
#RUN poetry config settings.virtualenvs.create false
#RUN poetry install --no-dev --no-ansi  #get an error
#COPY . /code/