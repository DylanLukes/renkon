sudo apt update
sudo apt install -y -V ca-certificates lsb-release wget
wget https://apache.jfrog.io/artifactory/arrow/$(lsb_release --id --short | tr 'A-Z' 'a-z')/apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt install -y -V ./apache-arrow-apt-source-latest-$(lsb_release --codename --short).deb
sudo apt update

sudo apt install -y -V liblz4-dev
sudo apt install -y -V libzstd-dev
sudo apt install -y -V libarrow-dev
sudo apt install -y -V libarrow-glib-dev
sudo apt install -y -V libparquet-dev
sudo apt install -y -V libparquet-glib-dev