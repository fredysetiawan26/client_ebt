From python:3.8

# Set environtment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFEERED 1

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY client_ebt.py /app

CMD python client_ebt.py
