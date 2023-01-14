execute_process(COMMAND "/media/psf/TO-DO_List/ros_chatbot/chatbot_ws/build/pepper_nodes/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/media/psf/TO-DO_List/ros_chatbot/chatbot_ws/build/pepper_nodes/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
