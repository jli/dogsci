#!/bin/bash

# adding -E by itself doesn't change anything. maybe because there's no default ERR trap?
# set -euo pipefail

# doesn't work. -T just for DEBUG/RETURN traps
# set -ETeuo pipefail
# echo "with ET"

# this works!
set -Eeuo pipefail
trap 'exit $?' ERR
echo "with big E and trap"

deploy() {
  echo deploying
  exit 1
}

deploy_caller() {
    # adding -e here does result in the 2nd thing failing like the 3rd
    # set -e
    local res
    res=$(deploy)
    echo "$res"
}

deploy_caller_caller() {
    local res
    res=$(deploy_caller)
    echo "$res"
}


# these are fine, for some reason
# echo deploy inline: "$(deploy)"
# echo deploy_caller inline: "$(deploy_caller)"

# fine, when there's extra indirection
echo setting var w deploy_caller_caller...
dcc="$(deploy_caller_caller)"
echo deploy_caller_caller result: "$dcc"

# fine, when there's extra indirection
echo setting var w deploy_caller...
dc="$(deploy_caller)"
echo deploy_caller result: "$dc"

# fails, when calling directly
echo setting var w deploy...
d="$(deploy)"
echo deploy result: "$d"
