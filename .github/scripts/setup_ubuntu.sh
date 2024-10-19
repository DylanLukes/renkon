sudo apt update
sudo apt install -y -V ca-certificates lsb-release wget
wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb

sudo apt update

# Based on: https://arrow.apache.org/install/
sudo apt install -y -\
  libre2-dev \
  libzstd-dev \
  liblz4-dev \
  libarrow-dev \
  libparquet-dev