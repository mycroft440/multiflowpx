#include "Worker.h"

// Worker implementation
Worker::Worker() : running_(false) {
}

Worker::~Worker() {
    stop();
}

void Worker::start() {
    if (running_) {
        return;
    }
    
    running_ = true;
    worker_thread_ = std::thread(&Worker::workerLoop, this);
}

void Worker::stop() {
    if (!running_) {
        return;
    }
    
    running_ = false;
    condition_.notify_all();
    
    if (worker_thread_.joinable()) {
        worker_thread_.join();
    }
}

bool Worker::isRunning() const {
    return running_;
}

void Worker::addTask(std::function<void()> task) {
    {
        std::lock_guard<std::mutex> lock(queue_mutex_);
        if (!running_) {
            return;
        }
        task_queue_.push(task);
    }
    condition_.notify_one();
}

size_t Worker::getQueueSize() const {
    std::lock_guard<std::mutex> lock(queue_mutex_);
    return task_queue_.size();
}

void Worker::workerLoop() {
    while (running_) {
        std::function<void()> task;
        
        {
            std::unique_lock<std::mutex> lock(queue_mutex_);
            condition_.wait(lock, [this] { return !task_queue_.empty() || !running_; });
            
            if (!running_) {
                break;
            }
            
            if (!task_queue_.empty()) {
                task = task_queue_.front();
                task_queue_.pop();
            }
        }
        
        if (task) {
            try {
                task();
            } catch (const std::exception& e) {
                std::cerr << "Worker task exception: " << e.what() << std::endl;
            } catch (...) {
                std::cerr << "Worker task unknown exception" << std::endl;
            }
        }
    }
}

// WorkerPool implementation
WorkerPool::WorkerPool(size_t num_workers) : next_worker_index_(0), running_(false) {
    workers_.reserve(num_workers);
    for (size_t i = 0; i < num_workers; ++i) {
        workers_.emplace_back(std::make_unique<Worker>());
    }
}

WorkerPool::~WorkerPool() {
    stop();
}

void WorkerPool::start() {
    if (running_) {
        return;
    }
    
    running_ = true;
    for (auto& worker : workers_) {
        worker->start();
    }
}

void WorkerPool::stop() {
    if (!running_) {
        return;
    }
    
    running_ = false;
    for (auto& worker : workers_) {
        worker->stop();
    }
}

bool WorkerPool::isRunning() const {
    return running_;
}

void WorkerPool::addTask(std::function<void()> task) {
    if (!running_) {
        return;
    }
    
    // Round-robin task distribution
    size_t worker_index = next_worker_index_.fetch_add(1) % workers_.size();
    workers_[worker_index]->addTask(task);
}

size_t WorkerPool::getTotalQueueSize() const {
    size_t total = 0;
    for (const auto& worker : workers_) {
        total += worker->getQueueSize();
    }
    return total;
}

size_t WorkerPool::getWorkerCount() const {
    return workers_.size();
}

