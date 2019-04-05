1 - Install packages on your buildserver

sudo apt-get install -y autoconf automake bison bzip2 curl cvs diffstat flex g++ gawk gcc gettext git-core gzip help2man ncurses-bin ncurses-dev libc6-dev libtool make texinfo patch perl pkg-config subversion tar texi2html wget zlib1g-dev chrpath libxml2-utils xsltproc libglib2.0-dev python-setuptools zip info coreutils diffstat chrpath libproc-processtable-perl libperl4-corelibs-perl sshpass default-jre default-jre-headless java-common libserf-dev qemu quilt libssl-dev

2 - Set your shell to /bin/bash.

sudo dpkg-reconfigure dash
When asked: Install dash as /bin/sh?
select "NO"

3 - Add user opennfrbuilder

sudo adduser opennfrbuilder

4 - Switch to user opennfrbuilder

su opennfrbuilder

5 - Switch to home of opennfrbuilder

cd ~

6 - Create folder opennfr

mkdir -p ~/opennfr

7 - Switch to folder opennfr

cd opennfr

8 - Clone oe-alliance git

git clone git://github.com/oe-alliance/build-enviroment.git -b 4.3

9 - Switch to folder build-enviroment

cd build-enviroment

10 - Update build-enviroment

make update

11 - Finally you can start building a image

MACHINE=mutant2400 DISTRO=opennfr DISTRO_TYPE=release make image


