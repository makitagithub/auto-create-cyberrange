FROM debian:buster
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y wget gnupg2 software-properties-common procps rsync xvfb

RUN wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox_2016.asc -O- | apt-key add - \
	&& wget -q http://download.virtualbox.org/virtualbox/debian/oracle_vbox.asc -O- | apt-key add - \
	&& apt-add-repository "deb http://download.virtualbox.org/virtualbox/debian buster contrib" \
	&& apt-get update \
	&& apt-get install -y virtualbox-6.1

RUN wget https://releases.hashicorp.com/vagrant/2.2.16/vagrant_2.2.16_x86_64.deb \
		&& dpkg -i vagrant_2.2.16_x86_64.deb

RUN apt-add-repository "deb http://ppa.launchpad.net/ansible/ansible/ubuntu trusty main" \
	&& apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 93C4A3FD7BB9C367 \
	&& apt-get update \
	&& apt-get install -y ansible

RUN apt-get update \
	&& apt-get install -y git python3-pip \
	&& pip3 install setuptools
