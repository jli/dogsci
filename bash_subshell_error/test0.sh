#!/bin/bash

# adding -E doesn't change anything
# set -euo pipefail
set -Eeuo pipefail
echo "with big E, no e"

deploy() {
  echo deploying
  exit 1
}

deploy_caller() {
    # adding -e here does result in the 2nd thing failing like the 3rd
    set -e
    local res
    res=$(deploy)
    echo "$res"
}

# these are fine, for some reason
echo deploy inline: "$(deploy)"
echo deploy_caller inline: "$(deploy_caller)"

# fine, when there's extra indirection
echo setting var w deploy_caller...
dc="$(deploy_caller)"
echo deploy_caller result: "$dc"

# fails, when calling directly
echo setting var w deploy...
d="$(deploy)"
echo deploy result: "$d"


# echo pre-deploy
# # this is fine, it echoes "deploy inline: deploying"
# echo deploy inline: "$(deploy)"
# echo deploy_caller inline: "$(deploy_caller)"
# echo setting var w deploy_caller...
# dc="$(deploy_caller)"  # this fails
# echo deploy_caller result: "$dc"
# echo setting var w deploy...
# d="$(deploy)"  # this fails
# echo deploy result: "$d"




# !/opt/homebrew/bin/bash
