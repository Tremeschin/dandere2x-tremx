# cd into where this file is located
cd ${BASH_SOURCE%/*}

# cd to dandere2x_cpp dir
cd ../dandere2x_cpp

# Clean previous cmake files
[ -e CMakeFiles ] && rm -r CMakeFiles
[ -e CMakeCache.txt ] && rm CMakeCache.txt
[ -e cmake_install.cmake ] && rm cmake_install.cmake

# Make
cmake CMakeLists.txt -DCOMPILE_FOR_LINUX_FROM_LINUX=True -DCMAKE_CXX_COMPILER=g++
make

# Remove and move old / new dandere2x executable
mkdir -p ../externals
[ -e ../externals/dandere2x_cpp ] && rm ../externals/dandere2x_cpp
mv dandere2x_cpp ../externals/dandere2x_cpp
