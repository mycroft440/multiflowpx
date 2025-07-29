#ifndef LOGGER_H
#define LOGGER_H

#include <iostream>
#include <string>
#include <chrono>
#include <iomanip>

// Macro para obter o tempo atual formatado
#define GET_TIMESTAMP() []() -> std::string {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}()

// Macros de logging
#define LOG_INFO(message) \ 
    std::cout << "[INFO] " << GET_TIMESTAMP() << " " << message << std::endl;

#define LOG_WARNING(message) \ 
    std::cerr << "[WARNING] " << GET_TIMESTAMP() << " " << message << std::endl;

#define LOG_ERROR(message) \ 
    std::cerr << "[ERROR] " << GET_TIMESTAMP() << " " << message << std::endl;

#endif // LOGGER_H


