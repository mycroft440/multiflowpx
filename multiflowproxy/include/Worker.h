#ifndef WORKER_H
#define WORKER_H

#include "Common.h"

class Worker {
public:
    Worker();
    ~Worker();
    
    void start();
    void stop();
    bool isRunning() const;
    
    template<typename Func>
    void execute(Func&& func) {
        {
            std::lock_guard<std::mutex> lock(queue_mutex_);
            if (!running_) {
                return;
            }
            task_queue_.emplace(std::forward<Func>(func));
        }
        condition_.notify_one();
    }
    
    void addTask(std::function<void()> task);
    size_t getQueueSize() const;
    
private:
    std::thread worker_thread_;
    std::queue<std::function<void()>> task_queue_;
    mutable std::mutex queue_mutex_;
    std::condition_variable condition_;
    std::atomic<bool> running_;
    
    void workerLoop();
};

// Worker Pool for managing multiple workers
class WorkerPool {
public:
    WorkerPool(size_t num_workers = Constants::DEFAULT_WORKERS);
    ~WorkerPool();
    
    void start();
    void stop();
    bool isRunning() const;
    
    template<typename Func>
    void submitTask(Func&& func) {
        if (!running_) {
            return;
        }
        
        // Round-robin task distribution
        size_t worker_index = next_worker_index_.fetch_add(1) % workers_.size();
        workers_[worker_index]->execute(std::forward<Func>(func));
    }
    
    void addTask(std::function<void()> task);
    size_t getTotalQueueSize() const;
    size_t getWorkerCount() const;
    
private:
    std::vector<std::unique_ptr<Worker>> workers_;
    std::atomic<size_t> next_worker_index_;
    std::atomic<bool> running_;
};

#endif // WORKER_H

