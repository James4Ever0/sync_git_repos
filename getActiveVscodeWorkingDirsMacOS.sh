# ps aux | grep /usr/lib/code-oss/code-oss | awk '{print $2}'| xargs -iabc pwdx  abc | awk '{print $2}'
function pwdx {
  lsof -a -d cwd -p $1 -n -Fn | awk '/^n/ {print substr($0,2)}'
}
# hint from https://gist.github.com/tobym/648188
# ps aux | grep /usr/lib/code-oss/code-oss | awk '{print $2}'| xargs -iabc pwdx  abc | awk '{print $2}'
