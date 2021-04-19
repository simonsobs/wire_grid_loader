#!/bin/bash
echo "This script will push all the changes to the remote repository in the current branch."
echo "Is it OK? If you are OK, please press the ENTER!"
read Wait
echo $Wait
echo "Please write the comment of this push."
read COMMENT
git add *;
git ci -m "${COMMENT}";
git push
