# cd into where this file is located
cd ${BASH_SOURCE%/*}

# cd to dandere2x_cpp dir
cd ../dandere2x_cpp

# Get OpenCV source file
git clone https://github.com/opencv/opencv

cd opencv

[ -e CMakeFiles ] && rm -r CMakeFiles
[ -e CMakeCache.txt ] && rm CMakeCache.txt
[ -e cmake_install.cmake ] && rm cmake_install.cmake

git pull
mkdir build
cd build

[ -e CMakeFiles ] && rm -r CMakeFiles
[ -e CMakeCache.txt ] && rm CMakeCache.txt
[ -e cmake_install.cmake ] && rm cmake_install.cmake

# Compile OpenCV
x86_64-w64-mingw32-cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=./

# Make and install
x86_64-w64-mingw32-make -j$(nproc)
x86_64-w64-mingw32-make install
