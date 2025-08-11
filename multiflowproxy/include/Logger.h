#ifndef LOGGER_H
#define LOGGER_H

#include <iostream>
#include <string>

// Macros de logging simplificadas
#define LOG_INFO(message) \
    std::cout << "[INFO] " << message << std::endl;

#define LOG_WARNING(message) \
    std::cerr << "[WARNING] " << message << std::endl;

#define LOG_ERROR(message) \
    std::cerr << "[ERROR] " << message << std::endl;

#endif // LOGGER_H

