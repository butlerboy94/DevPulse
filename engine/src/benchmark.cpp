#include "benchmark.h"

#include <algorithm>

#if defined(_WIN32)
#include <windows.h>
#include <psapi.h>
#elif defined(__linux__)
#include <cstdio>
#include <fstream>
#elif defined(__APPLE__)
#include <mach/mach.h>
#endif

namespace devpulse {

long long get_memory_usage() {
#if defined(_WIN32)
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return static_cast<long long>(pmc.WorkingSetSize);
    }
    return -1;
#elif defined(__linux__)
    std::ifstream status("/proc/self/status");
    std::string line;
    while (std::getline(status, line)) {
        if (line.rfind("VmRSS:", 0) == 0) {
            long long kb = 0;
            sscanf(line.c_str(), "VmRSS: %lld kB", &kb);
            return kb * 1024;
        }
    }
    return -1;
#elif defined(__APPLE__)
    mach_task_basic_info info;
    mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
    if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO,
                  reinterpret_cast<task_info_t>(&info), &count) == KERN_SUCCESS) {
        return static_cast<long long>(info.resident_size);
    }
    return -1;
#else
    return -1;
#endif
}

int detect_loop_depth(const std::vector<std::string>& tokens) {
    int max_depth     = 0;
    int current_depth = 0;
    for (const auto& token : tokens) {
        if (token == "for" || token == "while") {
            ++current_depth;
            if (current_depth > max_depth) max_depth = current_depth;
        } else if (token == "end_loop") {
            if (current_depth > 0) --current_depth;
        }
    }
    return max_depth;
}

} // namespace devpulse
