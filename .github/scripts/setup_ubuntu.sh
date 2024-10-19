sudo apt update
sudo apt install -y -V ca-certificates lsb-release wget
wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb

sudo apt update

sudo apt install -y -V \
  nvidia-cuda-toolkit

# Based on: https://arrow.apache.org/install/
sudo apt install -y -V \
  libre2-dev \
  libzstd-dev \
  liblz4-dev \
  libarrow-dev \
  libarrow-glib-dev \
  libarrow-acero-dev \
  libarrow-dataset-dev \
  libarrow-dataset-glib-dev \
  libarrow-flight-dev \
  libarrow-flight-glib-dev \
  libarrow-flight-sql-dev \
  libarrow-flight-sql-glib-dev \
  libarrow-cuda-dev \
  libgandiva-dev \
  libgandiva-glib-dev \
  libparquet-dev \
  libparquet-glib-dev