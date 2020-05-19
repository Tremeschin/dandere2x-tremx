# MAKE SURE OPENCV IS BUILT BEFORE RUNNING THIS SCRIPT

# cd into where this file is located
cd ${BASH_SOURCE%/*}

# Clean 
rm -r CMakeFiles
rm CMakeCache.txt
rm cmake_install.cmake

# Make
cmake -DCMAKE_TOOLCHAIN_FILE=./mingw-w64-x86_64.cmake CMakeLists.txt -DCMAKE_INSTALL_PREFIX=./ -DCROSS_COMPILE_FOR_WINDOWS_FROM_LINUX=True ..
make

# Remove and move old / new dandere2x executable
mkdir -p ../externals
rm ../externals/dandere2x_cpp.exe
mv dandere2x_cpp.exe ../externals/dandere2x_cpp.exe

# Copy every dll as we'll need them
cp opencv/build/bin/*.dll ../externals