FROM machina/base-alpine

COPY requirements.txt /tmp/
RUN pip3 install --trusted-host pypi.org \
                 --trusted-host pypi.python.org \
                 --trusted-host files.pythonhosted.org \
                 -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt