#!/bin/bash
PACKAGE_NAME=$1
VERSION=$2
PACKAGE_ARCH=$3
DIR_NAME="${PACKAGE_NAME}_${VERSION}-1_${PACKAGE_ARCH}"

rm -rf .package-build
mkdir .package-build
cd .package-build

# ------------------------------------------------------------

mkdir $DIR_NAME
mkdir -p $DIR_NAME/etc/presentium/presentium-client
mkdir -p $DIR_NAME/etc/systemd/system
mkdir -p $DIR_NAME/DEBIAN

# ------------------------------------------------------------

echo "Package: $PACKAGE_NAME
Version: $VERSION
Maintainer: <info@presentium.ch>
Depends: python3, python3-pip, python3-venv
Architecture: $PACKAGE_ARCH
Homepage: https://presentium.ch
Description: Presentium client app." \
> $DIR_NAME/DEBIAN/control

# ------------------------------------------------------------

echo "#!/bin/bash
cd /etc/presentium/presentium-client
python3 -m venv presentium-venv
. ./presentium-venv/bin/activate
pip3 install -r requirements.txt" \
python3 codegen.py \
> $DIR_NAME/DEBIAN/postinst
chmod 555 $DIR_NAME/DEBIAN/postinst

# ------------------------------------------------------------

# Main files
cp ../main.py $DIR_NAME/etc/presentium/presentium-client
cp ../requirements.txt $DIR_NAME/etc/presentium/presentium-client
cp ../codegen.py $DIR_NAME/etc/presentium/presentium-client

# Python modules
cp -r ../src $DIR_NAME/etc/presentium/presentium-client

# gRPC/protobuf protos
cp -r ../protos $DIR_NAME/etc/presentium/presentium-client

# Copy config files and create a default config.ini
cp -r ../config $DIR_NAME/etc/presentium/presentium-client
cp $DIR_NAME/etc/presentium/presentium-client/config/config.ini.default $DIR_NAME/etc/presentium/presentium-client/config/config.ini

# Copy systemd service file
cp ../presentium-client.service $DIR_NAME/etc/systemd/system

# ------------------------------------------------------------

dpkg --build $DIR_NAME
dpkg-deb --info $DIR_NAME.deb > "$DIR_NAME.deb.info"
dpkg-deb --contents $DIR_NAME.deb > "$DIR_NAME.deb.content"
