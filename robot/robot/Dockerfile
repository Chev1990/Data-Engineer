FROM base-image.dock.company.com/ubuntu/18.04/latest

LABEL dock.img.name="your-org.com/robot-tests-dq"  \
      dock.schema-version="0.1" \
      dock.maintainer.isid="blatov" \
      dock.maintainer.name="Aleksandr Blatov" \
      dock.maintainer.email="automation@company.com" \
      dock.maintainer.division="Automation" \
      dock.maintainer.team="Automation" \
      dock.img.description="Docker image for running Robot framework data quality tests" \
      dock.docker.run="docker run -it "

RUN echo "APT::Acquire::Retries \"5\";" > /etc/apt/apt.conf.d/80-retries

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.9 python3.9-dev python3.9-distutils wget

RUN wget -q https://bootstrap.pypa.io/get-pip.py && python3.9 get-pip.py

COPY requirements.txt .
COPY resources/libraries/ ./libraries/
RUN pip3.9 install -r requirements.txt && cd libraries && python3.9 setup.py install
