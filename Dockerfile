FROM python:3.8-slim-bullseye

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        libbz2-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        tk-dev \
        wget \
        xz-utils \
        zlib1g-dev \
        locales \
        libffi-dev \
        python3-venv \
        python3-dev \
        procps
        
RUN echo 'vm.overcommit_memory=1' >> /etc/sysctl.conf

RUN sed -i '/it_IT.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG it_IT.UTF-8  
ENV LANGUAGE it_IT:it  
ENV LC_ALL it_IT.UTF-8

#RUN useradd -ms /bin/bash uwsgi
#USER uwsgi

ENV PATH="/home/uwsgi/.local/bin:${PATH}"

COPY requirements.txt .

RUN pip3 install -r requirements.txt

#USER root
WORKDIR /app

COPY .env .
COPY iren.py .
COPY main.py .
COPY uwsgi.ini .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
#RUN chown -R uwsgi:uwsgi /app

#USER uwsgi
#WORKDIR /app

CMD ["./entrypoint.sh"]
#CMD . .venv/bin/activate && exec flask run main.py --host=0.0.0.0
