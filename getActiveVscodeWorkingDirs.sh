ps aux | grep /usr/lib/code-oss/code-oss | awk '{print $2}'| xargs -iabc pwdx  abc | awk '{print $2}'
