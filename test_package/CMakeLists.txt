cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_VERBOSE_MAKEFILE ON)

option(ENABLE_PROTOC "Run protoc to generate sources" ON)
set(OPTIMIZED_FOR "SPEED" CACHE STRING "optimized_for")

find_package(protobuf CONFIG REQUIRED)
message(STATUS "Using Protocol Buffers ${protobuf_VERSION}")
set(CMAKE_INCLUDE_CURRENT_DIR TRUE)

# http://www.cmake.org/Wiki/CMake_FAQ#How_can_I_build_my_MSVC_application_with_a_static_runtime.3F
if(MSVC AND protobuf_MSVC_STATIC_RUNTIME)
  foreach(flag_var
      CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
      CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
    if(${flag_var} MATCHES "/MD")
      string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
    endif(${flag_var} MATCHES "/MD")
  endforeach()
endif()

set(TEST_SRCS test_package.cpp)

if (ENABLE_PROTOC)
    configure_file(addressbook.proto.in "${CMAKE_SOURCE_DIR}/addressbook.proto" @ONLY)

    set(TEST_PROTOS addressbook.proto)

    #Code Generation
    if(protobuf_MODULE_COMPATIBLE) #Legacy Support
        protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS ${TEST_PROTOS})
        list(APPEND TEST_SRCS ${PROTO_SRCS} ${PROTO_HDRS})
    endif()

    if(BUILD_SHARED_LIBS)
        add_definitions(PROTOBUF_USE_DLLS)
    endif()

    #Executable setup
    add_executable(${PROJECT_NAME} ${TEST_SRCS} ${TEST_PROTOS})
    if(protobuf_MODULE_COMPATIBLE) #Legacy mode
        target_include_directories(${PROJECT_NAME} PRIVATE ${PROTOBUF_INCLUDE_DIRS})
        target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
    else()
        if (UNIX)
            target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
        else()
            target_link_libraries(${PROJECT_NAME} CONAN_PKG::protobuf)
        endif()
        protobuf_generate(TARGET ${PROJECT_NAME})
    endif()
else (ENABLE_PROTOC)
    set(TEST_PROTOS addressbook.pb.cc addressbook.pb.h)
    add_executable(${PROJECT_NAME} ${TEST_SRCS} ${TEST_PROTOS})
    target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
    target_include_directories(${PROJECT_NAME} PRIVATE ${PROTOBUF_INCLUDE_DIRS} /home/uilian/.conan/data/protoc_installer/3.6.1/bincrafters/stable/package/44fcf6b9a7fb86b2586303e3db40189d3b511830/include)
endif (ENABLE_PROTOC)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)