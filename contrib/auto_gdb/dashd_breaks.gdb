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
