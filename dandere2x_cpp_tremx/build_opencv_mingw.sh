# cd into where this file is located
cd ${BASH_SOURCE%/*}

# Get OpenCV source file
git clone https://github.com/opencv/opencv

cd opencv
#git pull
mkdir build
cd build

# Compile OpenCV
x86_64-w64-mingw32-cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./

# Make and install
x86_64-w64-mingw32-make -j$(nproc)
x86_64-w64-mingw32-make install
