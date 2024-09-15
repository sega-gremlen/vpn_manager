FROM python:3.12

#RUN mkdir /vpn_manager

WORKDIR /vpn_manager

COPY req.txt .

ENV PYTHONPATH="${PYTHONPATH}:/vpn_manager"

RUN pip --no-cache-dir install -r req.txt

COPY . .

RUN chmod a+x docker_commands.sh

ENV TZ="Europe/Moscow"

#ENTRYPOINT ["/vpn_manager/docker_commands.sh"]
