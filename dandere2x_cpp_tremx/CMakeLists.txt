cmake_minimum_required(VERSION 2.8)
project( dandere2x_cpp )


find_package( OpenCV REQUIRED )

set(CMAKE_BUILD_TYPE Release)

set(CMAKE_CXX_FLAGS_RELEASE "-O3")

set_property(TARGET PROPERTY CXX_STANDARD 17)

add_executable( dandere2x_cpp main.cpp )
target_link_libraries( dandere2x_cpp ${OpenCV_LIBS} )
