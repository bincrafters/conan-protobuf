cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PkgConfig REQUIRED)
find_package(Protobuf REQUIRED)
pkg_check_modules(Protobuf REQUIRED Protobuf)

PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)

target_link_libraries(${PROJECT_NAME} ${PROTOBUF_LIBRARIES})
target_include_directories(${PROJECT_NAME} PUBLIC ${PROTOBUF_INCLUDE_DIRS})
target_compile_options(${PROJECT_NAME} PUBLIC ${PROTOBUF_CFLAGS_OTHER})


# find_package(Protobuf REQUIRED)
# PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)

# message("CONAN_LIBS >>> ${CONAN_LIBS}")
# message("PROTOBUF_LIBRARY >>> ${PROTOBUF_LIBRARY}")

# include_directories(${CMAKE_CURRENT_BINARY_DIR})
# add_executable(${PROJECT_NAME} test_package.cpp addressbook.pb.cc addressbook.pb.h)
# target_link_libraries(${PROJECT_NAME} ${PROTOBUF_LIBRARY})

