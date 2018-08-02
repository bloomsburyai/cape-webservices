#This image runs Cape :
# You can run cape in 3 different modes :
# * Standalone :    docker run ...
# * As a Master,Scheduler and Worker(s):
#   * Master:       docker run ...
#   * Scheduler:    docker run ...
#   * Worker(s):    docker run ...

FROM ubuntu:18.04

RUN apt-get -y update && \
    apt-get install -y python-dev python3-dev python3-pip git zlib1g-dev\
                       apt-transport-https ca-certificates wget build-essential\
                       libcurl4-openssl-dev g++ htop nano parallel curl locales\
                       daemontools unzip python3-distutils && \
    apt-get clean

RUN pip3 install --upgrade pip setuptools dumb-init ipython

# Ensure that we always use UTF-8 and with US English locale
RUN locale-gen en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV PYTHONIOENCODING utf-8

#Add non-root user to run app
RUN useradd -G users -m runner

WORKDIR /mnt/
#Argument to rebuild from this point after an update
ARG COMMIT_SHA1=1
RUN pip3 install -vv --process-dependency-links --upgrade git+https://github.com/bloomsburyai/cape-webservices
#Run model tests to automatically download latest standard production model
RUN pytest -vs --pyargs cape_document_qa.tests
EXPOSE 5050

#Default configuration
ENV PORT 5050

ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]

CMD ["bash" ,"-c", "python3 -m cape_webservices.run $PORT" ]

#docker stop my_service;docker rm my_service;docker build -t my_service_image -f deployment/Dockerfile . && docker run -ti --ulimit core=0:0 --user runner --rm -v $(pwd)/..:/mnt --name my_service my_service_image
