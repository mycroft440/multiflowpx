#ifndef LOGGER_H
#define LOGGER_H

#include <iostream>
#include <ctime>

#define LOG_INFO(msg) std::cout << "[" << time(NULL) << "] INFO: " << msg << std::endl
#define LOG_WARNING(msg) std::cerr << "[" << time(NULL) << "] WARNING: " << msg << std::endl
#define LOG_ERROR(msg) std::cerr << "[" << time(NULL) << "] ERROR: " << msg << std::endl

#endif // LOGGER_H
