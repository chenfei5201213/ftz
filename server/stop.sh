ps aux | grep 'gun' | grep -v 'grep' | awk '{print $2}' | xargs kill
ps aux | grep 'beta' | grep -v 'grep' | awk '{print $2}' | xargs kill
ps aux | grep 'worker' | grep -v 'grep' | awk '{print $2}' | xargs kill