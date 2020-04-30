
# cd into where this file is located
cd ${BASH_SOURCE%/*}

# Warn the user
printf "  Make sure you have cmake and a compiler (g++ preferred)\n"

# Generate build files
printf "  Cmake\n"
cmake CMakeLists.txt

# Compile the binary
printf "  Make\n"
make

# cd into root dandere2x folder
cd ..

# Make directory "externals" if it doesn't exist
printf "  Make directory externals if it doesn't exist.. "
mkdir -p externals
printf "ok\n"

# Move the dandere2x_cpp binary into it
printf '  Moving binary.. '
mv "dandere2x_cpp_tremx/dandere2x_cpp" "externals/dandere2x_cpp"
printf "ok\n"
