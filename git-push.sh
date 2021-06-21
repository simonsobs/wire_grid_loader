#!/bin/bash
echo "This script will push all the changes to the remote repository in the current branch."
echo "Is it OK? Please press the ENTER to proceed, or Ctrl+C to exit."
read Wait
echo $Wait

if [ $# = 1 ]; then
    COMMENT=$1
else
    echo "Please write the comment of this push."
    read COMMENT
fi

echo "Check in comment: $COMMENT"

git add *;
git ci -m "${COMMENT}";
git push
