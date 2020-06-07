# MAKE SURE OPENCV IS BUILT BEFORE RUNNING THIS SCRIPT

# cd into where this file is located
cd ${BASH_SOURCE%/*}

# cd to dandere2x_cpp dir
cd ../dandere2x_cpp

# Clean previous cmake files
[ -e CMakeFiles ] && rm -r CMakeFiles
[ -e CMakeCache.txt ] && rm CMakeCache.txt
[ -e cmake_install.cmake ] && rm cmake_install.cmake

# Make
cmake -DCMAKE_TOOLCHAIN_FILE=./mingw-w64-x86_64.cmake CMakeLists.txt -DCMAKE_INSTALL_PREFIX=./ -DCROSS_COMPILE_FOR_WINDOWS_FROM_LINUX=True ..
make

# Remove and move old / new dandere2x executable
mkdir -p ../externals
[ -e ../externals/dandere2x_cpp.exe ] && rm ../externals/dandere2x_cpp.exe
mv dandere2x_cpp.exe ../externals/dandere2x_cpp.exe

# Copy every dll as we'll need them
cp opencv/build/bin/*.dll ../externals