#ifndef MEMORY_LOGGER_H
#define MEMORY_LOGGER_H

#include <string>
#include <chrono>
#include <map>
#include <thread>
#include <mutex>
#include <boost/function.hpp>


class memory_logger
{
public:
    typedef boost::function<size_t(void)> entry;

    static memory_logger* get_instance();

    memory_logger() = delete;
    memory_logger(const memory_logger&) = delete;
    memory_logger(memory_logger&&) = delete;
    memory_logger& operator=(const memory_logger&) = delete;

    ~memory_logger();

    void add(const std::string& key, entry e);
    void event(const std::string& event_descr);
private:
    memory_logger(const std::string& common_file,
                  const std::string& details_file,
                  const std::string& events_file,
                  const std::chrono::duration<int>& query_period);

    void run();

    std::string common_file_;
    std::string details_file_;
    std::string events_file_;
    std::chrono::duration<int> query_period_;

    std::map<std::string, entry> entries_;
    std::thread worker_;
    std::atomic_flag stop_flag_;
    std::mutex entries_lock_;
    std::mutex common_lock_;
    std::mutex events_lock_;
};

#endif // MEMORY_LOGGER_H
