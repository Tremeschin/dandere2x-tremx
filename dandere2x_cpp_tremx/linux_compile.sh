# cd into where this file is located
cd ${BASH_SOURCE%/*}

# Clean
rm -r CMakeFiles
rm CMakeCache.txt
rm cmake_install.cmake

# Make
cmake CMakeLists.txt -DCOMPILE_FOR_LINUX_FROM_LINUX=True -DCMAKE_CXX_COMPILER=g++
make

# Remove and move old / new dandere2x executable
mkdir -p ../externals
rm ../externals/dandere2x_cpp
mv dandere2x_cpp ../externals/dandere2x_cpp
