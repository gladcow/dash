define test_used_size
	set $size_ext = 0
	usedsize $size_ext $arg0
	p $size_ext
end

define set_dashd_breaks
    set pagination off
    set logging file memlog.txt
    set logging on
    b net_processing.cpp:2172
    commands
        bt
        usedsize mnodeman
        continue
    end
end

define check_value
    set $diff = 1
    while ($diff < 100)
        set $test = $value + $diff
        set $map = *('std::map<CNetAddr, long, std::less<CNetAddr>, std::allocator<std::pair<CNetAddr const, long> > >'*)$test
        set $size = $map._M_t._M_impl._M_node_count
        if($size == 7)
            p $diff
            p $size
        end
        set $diff = $diff + 1
    end
end