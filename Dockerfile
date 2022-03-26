# Reference: https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
FROM python:3.9-slim

ENV SRC_DIR="/opt/football_analytics"
ENV VIRTUAL_ENV="/opt/venv"
ENV DATA_DIR="/opt/data"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

VOLUME [ "${DATA_DIR}" ]

RUN python3 -m venv "$VIRTUAL_ENV"

RUN mkdir -p "$SRC_DIR" 

WORKDIR "${SRC_DIR}"

COPY requirements.txt "${SRC_DIR}/" 

RUN pip install --upgrade pip \
  && pip install -r requirements.txt

COPY src "${SRC_DIR}/" 

ENTRYPOINT [ "python", "-m", "main" ]
