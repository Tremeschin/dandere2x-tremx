# Master options
project( dandere2x_cpp )
cmake_minimum_required(VERSION 3.17)
set( CMAKE_CXX_STANDARD 17 )
set_property( TARGET PROPERTY CXX_STANDARD 17 )

# Linux
if ( DEFINED COMPILE_FOR_LINUX_FROM_LINUX )

	message( STATUS "Compiling for Linux, native" )

	find_package( OpenCV REQUIRED )
	include_directories( ${OpenCV_INCLUDE_DIRS} )
	add_executable( dandere2x_cpp main.cpp )
	target_link_libraries( dandere2x_cpp ${OpenCV_LIBS} )

# Cross compile Windows from Linux
# Make sure OpenCV is already built
elseif( DEFINED CROSS_COMPILE_FOR_WINDOWS_FROM_LINUX )

	message( STATUS "Cross compiling for Windows on Linux with MinGW" )

	set( CMAKE_CXX_STANDARD_LIBRARIES "-static-libgcc -static-libstdc++" )
	set( CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++ -static" )
	set( OpenCV_STATIC ON )
	set( OpenCV_DIR ${CMAKE_CURRENT_SOURCE_DIR}/opencv/build )
	include_directories( ${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/include/opencv4 )
	include_directories( ${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/include )
	link_directories( ${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib )
	link_directories ( ${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib )
	find_package( OpenCV REQUIRED )
	add_executable( dandere2x_cpp main.cpp )

	# Link
	target_link_libraries( dandere2x_cpp
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_core430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_dnn430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_features2d430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_flann430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_gapi430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_highgui430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_imgcodecs430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_imgproc430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_ml430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_objdetect430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_photo430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_stitching430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_video430.dll.a
		${CMAKE_CURRENT_SOURCE_DIR}/opencv/build/lib/libopencv_videoio430.dll.a
	)

endif()

# Release options
set( CMAKE_SHARED_LIBRARY_LINK_CXX_FLAGS )
set( CMAKE_BUILD_TYPE Release )
set( CMAKE_CXX_FLAGS_RELEASE "-O3" )
