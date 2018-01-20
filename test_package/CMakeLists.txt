cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(protobuf REQUIRED)
find_program(Protobuf_PROTOC_EXECUTABLE
    NAMES protoc
    DOC "The Google Protocol Buffers Compiler"
    PATHS
    ${CONAN_BIN_DIRS_PROTOBUF})
mark_as_advanced(Protobuf_PROTOC_EXECUTABLE)
PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)

# Static runtime
foreach(flag_var
        CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
    if(${flag_var} MATCHES "/MD")
        string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
    endif()
endforeach()

# Add executable
link_directories(${CONAN_LIB_DIRS})  # TODO: Get library with full path to avoid this command.
add_executable(${PROJECT_NAME} test_package.cpp ${PROTO_SRCS} ${PROTO_HDRS})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_BINARY_DIR})  # TODO: target dir for .pb.h files.
