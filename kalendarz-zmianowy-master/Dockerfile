FROM python:3.9-slim-buster
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install blinker
RUN pip install bson
RUN pip install cffi
RUN pip install click
RUN pip install colorama
RUN pip install cryptography
RUN pip install dnspython
RUN pip install Flask
RUN pip install itsdangerous
RUN pip install Jinja2
RUN pip install jwt
RUN pip install MarkupSafe
RUN pip install pycparser
RUN pip install PyJWT
RUN pip install pymongo
RUN pip install python-dateutil
RUN pip install six
RUN pip install Werkzeug
RUN pip install flasgger
RUN pip install flask_cors

COPY . .
EXPOSE 5000
ENV FLASK_APP=api.py
CMD ["flask", "run", "--host", "0.0.0.0"]