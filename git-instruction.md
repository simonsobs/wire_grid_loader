# Git Instruction

Github help web page: https://docs.github.com/en/github
Git help web page: https://git-scm.com/book/en/v2

## Overview of git
There are three stages to keep youre codes.
- **A**: Local codes (in your PC)
- **B**: Local branch in the local repository (in your PC)
    - The local repository also keeps all the history of the code changes occurred in your PC.
- **C**: Remote branch in the remote repository (in the github web page: https://github.com/simonsobs/wire\_grid\_loader)

If you want to save your change of the codes in the remote, 
you need to do 3 steps.

1. Change your code locally in **A**.
2. Add and commit your change in the local branch(**B**).
3. Push your change in the local branch to the remote branch(**C**).

You can create multiple branches in **B** and **C**.  
However, usually you just need to use ``master`` branch.

## Common git commands
Ref.: https://docs.github.com/en/github/using-git/using-common-git-commands

### Upload your local change in **A** to the remote branch(**C**)
1. Add your files to be updated to the local branch (**B**)  
   (to add all the files in the current directory)   

          git add .
          
    or (to add a spefic file)  

          git add <FILE NAME>

2. Update the changes to the local branch (**B**) with a comment  

        git commit -m "<COMMENT>"

    or  

        git ci -m "<COMMENT>"

    (``ci`` is an alias of ``commit``)
3. Update the changes from the local branch (**B**) to the remote branch (**C**)
   Ref.: https://docs.github.com/en/github/using-git/pushing-commits-to-a-remote-repository  
  
        git push

    or

        git push <REMOTE NAME> <LOCAL BRNCH NAME>

    Usually,
     - ``<REMOTE NAME>`` (**C**) is ``origin``, and
     - ``<LOCAL BRANCH NAME>`` (**B**) is ``master``.
     In this case, the master branch in **B** is uploaded to the master branch in **C**.
  
## Get changes in remote repository
Ref.: https://docs.github.com/en/github/using-git/getting-changes-from-a-remote-repository  

Shortcut command:
1. Get the changes in the remote repository (**A**) and merge it into your local master branch (**A**)  
    
        git pull

    or

        git pull <REMOTE NAME>/<REMOTE BRANCH NAME>

    Usually,
     - ``<REMOTE NAME>`` is ``origin``, and 
     - ``<REMOTE BRANCH NAME>`` is ``master``.


The ``push`` command does the following 2 steps;
1. Get the remote changes  

        git fetch 
        
    or
        
        git fetch <REMOTE NAME>

    Usually, ``<REMOTE NAME>`` is ``origin``.

2. Merge the changes in remote repository (C) into the local branch (B) (current local branch)   

        git merge <REMOTE NAME>/<REMOTE BRANCH NAME>

    * The data of the remote repository is kept also in your PC when you fetch it. The remote repository in your PC is not edited.



### Check the branch information
- Check only the local branch (**B**)  

        git branch

- Check the remote branch information (**C**)  

        git remote -v

- Check the local and remote branches (**B** & **C**)  

        git branch -a

  * This command shows the information of the remote branches fetched into your PC.


    
