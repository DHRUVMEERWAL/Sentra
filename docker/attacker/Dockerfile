FROM alpine:latest

RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing --repository http://dl-cdn.alpinelinux.org/alpine/edge/community hping3 && \
    apk add --no-cache curl netcat-openbsd bash python3 py3-pip && \
    pip install scapy --break-system-packages

WORKDIR /app
COPY attack.sh .
COPY generate_traffic.py .
RUN chmod +x attack.sh

CMD ["bash", "attack.sh"]
