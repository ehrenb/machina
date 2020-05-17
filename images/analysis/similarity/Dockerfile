FROM machina/base-alpine3

# Install ssdeep library
RUN cd /tmp && \
    wget https://github.com/ssdeep-project/ssdeep/releases/download/release-2.14.1/ssdeep-2.14.1.tar.gz && \
    tar -zxvf ssdeep-2.14.1.tar.gz && \
    cd ssdeep-2.14.1 && \
    ./configure && \
    make && \
    make install && \
    rm -rf /tmp/ssdeep-2.14.1

COPY requirements.txt /tmp/
RUN pip3 install --trusted-host pypi.org \
                 --trusted-host pypi.python.org \
                 --trusted-host files.pythonhosted.org \
                 -r /tmp/requirements.txt
RUN rm /tmp/requirements.txt