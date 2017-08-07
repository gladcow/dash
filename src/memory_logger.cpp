#include "memory_logger.h"
#include "tinyformat.h"
#include <boost/bind.hpp>
#include <fstream>

memory_logger* memory_logger::get_instance()
{
    // instance_s creation is thread-safe in C++11
    static memory_logger instance_s(
                    "/home/sergey/dash/ml_common.txt",
                    "/home/sergey/dash/ml_detail.txt",
                    "/home/sergey/dash/ml_events.txt",
                    std::chrono::seconds(5));
    return &instance_s;
}

memory_logger::memory_logger(const std::string& common_file,
                             const std::string& details_file,
                             const std::string& events_file,
                             const std::chrono::duration<int>& query_period):
    common_file_(common_file),
    details_file_(details_file),
    events_file_(events_file),
    query_period_(query_period)
{
    event("ctor");
    stop_flag_.test_and_set();
    worker_ = std::thread(boost::bind(&memory_logger::run, this));
}

memory_logger::~memory_logger()
{
    event("dtor");
    stop_flag_.clear();
    worker_.join();
}

void memory_logger::add(const std::string &key, entry e)
{
    std::lock_guard<std::mutex> lock(entries_lock_);
    entries_[key] = e;
    event(strprintf("add %s, entries %d", key.c_str(), entries_.size()));
}

void memory_logger::event(const std::string& event_descr)
{
    std::lock_guard<std::mutex> lock(events_lock_);
    std::ofstream out(events_file_, std::ios_base::app);
    if(out.is_open())
        out <<
           std::chrono::system_clock::now().time_since_epoch().count() <<
           "," << event_descr << std::endl;
}

void memory_logger::run()
{
    while(stop_flag_.test_and_set())
    {
        std::this_thread::sleep_for(query_period_);
        size_t sum = 0;
        {
            std::ofstream out(details_file_, std::ios_base::app);
            std::lock_guard<std::mutex> lock(entries_lock_);
            event(strprintf("entries: %d", entries_.size()));
            for(auto p: entries_)
            {
                try
                {
                    size_t s = p.second();
                    if(out.is_open())
                        out <<
                           std::chrono::system_clock::now().time_since_epoch().count() <<
                           "," << p.first << "," << s << std::endl;
                    sum += s;
                }
                catch(const std::exception& e)
                {
                    event(strprintf("Error while processing %s: %s", p.first.c_str(), e.what()));
                }
                catch(...)
                {
                    event(strprintf("Unknown error while processing %s", p.first.c_str()));
                }
            }
        }
        std::lock_guard<std::mutex> lock(common_lock_);
        std::ofstream out(common_file_, std::ios_base::app);
        if(out.is_open())
            out <<
               std::chrono::system_clock::now().time_since_epoch().count() <<
               "," << sum << std::endl;
    }
}
