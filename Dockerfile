FROM ubuntu:latest
LABEL authors="kasca"

ENTRYPOINT ["top", "-b"]