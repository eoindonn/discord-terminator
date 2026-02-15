#!/bin/bash
set -e

APP_NAME="DiscordTerminator"
VERSION="1.0.0"
APP_DIR="AppDir"
EXECUTABLE="dist/DiscordTerminator"

echo "Creating AppImage structure..."

# 1. Clear and Create AppDir
rm -rf $APP_DIR
mkdir -p $APP_DIR/usr/bin
mkdir -p $APP_DIR/usr/share/icons/hicolor/1024x1024/apps

# 2. Copy the PyInstaller executable
cp $EXECUTABLE $APP_DIR/usr/bin/discord-terminator

# 3. Copy icon
cp icon.png $APP_DIR/discord-terminator.png
cp icon.png $APP_DIR/usr/share/icons/hicolor/1024x1024/apps/discord-terminator.png

# 4. Create Desktop File
cat <<EOF > $APP_DIR/discord-terminator.desktop
[Desktop Entry]
Type=Application
Name=Discord Terminator
Exec=discord-terminator
Icon=discord-terminator
Categories=Network;Chat;
Comment=Discord to Stoat Migration Tool
Terminal=false
EOF

# 5. Create AppRun script
cat <<EOF > $APP_DIR/AppRun
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
export PATH="\$HERE/usr/bin:\$PATH"

# Enable Wayland support for Qt if the session is Wayland
if [ "\$XDG_SESSION_TYPE" == "wayland" ]; then
    export QT_QPA_PLATFORM=wayland
else
    export QT_QPA_PLATFORM=xcb
fi

# Fix for some distros where Qt looks for plugins in the wrong place
export QT_PLUGIN_PATH="\$HERE/usr/bin"

exec discord-terminator "\$@"
EOF
chmod +x $APP_DIR/AppRun

# 6. Download appimagetool if not present
if [ ! -f appimagetool ]; then
    echo "Downloading appimagetool..."
    curl -Lo appimagetool https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool
fi

# 7. Generate AppImage
export ARCH=x86_64
./appimagetool $APP_DIR

echo "AppImage created successfully!"
