FROM machina/base-alpine

RUN apk --update add --no-cache libmagic tiff-dev jpeg-dev openjpeg-dev zlib-dev

COPY requirements.txt /tmp/
RUN pip3 install --trusted-host pypi.org \
                --trusted-host pypi.python.org \
                --trusted-host files.pythonhosted.org \
                -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt

COPY src /machina/src