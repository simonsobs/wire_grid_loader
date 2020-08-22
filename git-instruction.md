# Git Instruction

Github help web page: https://docs.github.com/en/github

## Overview of git
There are three stages to keep youre codes.
A Local codes (in your computer)
B Local branch (in your computer)
C Remote branch (in the github web page: https://github.com/simonsobs/wire\_grid\_loader)

If you want to save your change of the codes in the remote, 
you need to do 3 steps.

1. Change your code locally in A.
2. Add and commit your change in the local branch(B).
3. Push your change in the local branch to the remote branch(C).

## Common git commands
Ref.: https://docs.github.com/en/github/using-git/using-common-git-commands

### To upload your local change in A to the remote branch(C)
1. Add your files to be updated to the local branch (B)  
   (to add all the files in the current directory)   
          git add .
    or (to add a spefic file)  
          git add <file name>
2. Update the changes to the local branch (B) with a comment  
        git commit -m "<comment>"
    or  
        git ci -m "<comment>"
    ('ci' is an alias of 'commit')
  
    
