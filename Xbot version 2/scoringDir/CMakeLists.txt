cmake_minimum_required(VERSION 3.10)

# Set the project name
project(MyXlntScript)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_PREFIX_PATH "C:\Users\USER\Desktop\Scraper API\scoringDir\src\xlnt\include\xlnt")


# Add the executable
add_executable(score_script "./src/main.cpp")


set(BUILD_SHARED_LIBS OFF)


# Find the Xlnt package
find_package(xlnt REQUIRED)

# Link Xlnt to your executable
target_link_libraries(score_script PRIVATE xlnt::xlnt)
