FROM python:3.12.9

WORKDIR /app

COPY requirements.txt .

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./super_researcher /app


CMD ["adk", "run", "SuperResearcher"]
