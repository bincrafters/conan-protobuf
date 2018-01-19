cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
#conan_basic_setup()

message(" >>>> ${CONAN_LIB_DIRS_PROTOBUF}/pkgconfig")
set(ENV{PKG_CONFIG_PATH}  "${CONAN_LIB_DIRS_PROTOBUF}/pkgconfig")
find_package(PkgConfig REQUIRED)
pkg_search_module(PCK_PROTOBUF REQUIRED protobuf)

#PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)
#target_link_libraries(${PROJECT_NAME} ${PROTOBUF_LIBRARIES})
#target_include_directories(${PROJECT_NAME} PUBLIC ${PROTOBUF_INCLUDE_DIRS})
#target_compile_options(${PROJECT_NAME} PUBLIC ${PROTOBUF_CFLAGS_OTHER})

#find_package(Protobuf REQUIRED)
#find_package(Threads)
#PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)

#message("CONAN_LIBS >>> ${CONAN_LIBS}")
# message("PROTOBUF_LIBRARY >>> ${PROTOBUF_LIBRARY}")

include_directories(${CONAN_INCLUDE_DIRS_PROTOBUF})
add_executable(${PROJECT_NAME} test_package.cpp addressbook.pb.cc addressbook.pb.h)
target_link_libraries (${PROJECT_NAME} ${PCK_PROTOBUF_LDFLAGS})
message("PCK_PROTOBUF_LDFLAGS >>> ${PCK_PROTOBUF_LDFLAGS}")
message("PKG_PROTOBUF_INCLUDE_DIRS >>> ${PKG_PROTOBUF_INCLUDE_DIRS}")


#add_executable(${PROJECT_NAME} test_package.cpp addressbook.pb.cc addressbook.pb.h)
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
#target_link_libraries(${PROJECT_NAME} ${PROTOBUF_LIBRARY})

