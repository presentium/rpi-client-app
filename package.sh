#!/bin/bash
PACKAGE_NAME=$1
VERSION=$2
PACKAGE_ARCH=$3
DIR_NAME="${PACKAGE_NAME}_${VERSION}-1_${PACKAGE_ARCH}"

rm -rf .package-build
mkdir .package-build
cd .package-build

mkdir $DIR_NAME
mkdir -p $DIR_NAME/etc/presentium/presentium-client
mkdir -p $DIR_NAME/etc/systemd/system
mkdir -p $DIR_NAME/DEBIAN

echo "Package: $PACKAGE_NAME
Version: $VERSION
Maintainer: <info@presentium.ch>
Depends: python3
Architecture: $PACKAGE_ARCH
Homepage: https://presentium.ch
Description: Presentium client app." \
> $DIR_NAME/DEBIAN/control

echo "#!/bin/bash
python3 -m pip install -r requirements.txt" \
> $DIR_NAME/DEBIAN/postinst
chmod 555 $DIR_NAME/DEBIAN/postinst

cp ../main.py $DIR_NAME/etc/presentium/presentium-client
cp ../requirements.txt $DIR_NAME/etc/presentium/presentium-client

cp ../presentium-client.service $DIR_NAME/etc/systemd/system

dpkg --build $DIR_NAME
dpkg-deb --info $DIR_NAME.deb > "$DIR_NAME.deb.info"
dpkg-deb --contents $DIR_NAME.deb > "$DIR_NAME.deb.content"
