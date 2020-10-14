# Git Instruction
**Current git account is set to sadachi5 (Shunsuke Adachi).
So all the commits are recorded to be done by sadachi5.**

Github help web page: https://docs.github.com/en/github
Git help web page: https://git-scm.com/book/en/v2

## Overview of git
There are three stages to keep youre codes.
- **A**: Local codes (in your PC)
- **B**: Local branch in the local repository (in your PC)
    - The local repository also keeps all the history of the code changes occurred in your PC.
- **C**: Remote branch in the remote repository (in the github web page: https://github.com/simonsobs/wire_grid_loader)

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
  
### Get changes in remote repository
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


    



# Creating New Repository & Setting Git
## Creating new repository
Here, the situation is that you want to create a new git repository and uploaded exsisting codes in your PC to the new repository.    

1. Create a new repository in the simons observatory git hub account: https://github.com/simonsobs

2. Get your git repsository copy address: ``git@github.com:simonsobs/wire_grid_loader.git``   
    - This can be obtained in the Code bottom in the top page of the git repository web page. https://github.com/simonsobs/wire_grid_loader
    - There are two kinds of address;
      1. HTTPS address
      2. ssh address  

      The HTTPS address cannot use the ssh public key authentification and you need to type your username&password every time you want to push or pull from the remote repository. 
      
    
    

3. In your PC, move to the top directory of the scripts to be uploaded to git   

4. Make ``README.md``

        echo "# <REPOSITORY NAME>" >> README.md

5. Initilize your git repository in your PC  

        git init
        git add . (including your exsited scripts)
        git commit -m "<COMMENT>"
        git remote add origin <GIT REPOSITORY ADDRESS>
        git push -u origin master

    ``<GIT REPOSITORY ADDRESS>`` is git@github.com:simonsobs/wire_grid_loader.git for the wire_grid_loader repository.

## Customization
### ssh setting
Ref. : https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh
        
1. Generate ssh public key

        ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

   * The public key file should be ``id_rsa.pub``

2. Add the public key to your git account  
    Ref.: https://docs.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account
    


### git command alias
Ref.: https://git-scm.com/book/en/v2/Git-Basics-Git-Aliases

Set git commands alias;
  - commit   --> ci
  - checkout --> co
  - branch   --> br
  - status   --> st

        git config --global alias.co checkout
        git config --global alias.br branch
        git config --global alias.ci commit
        git config --global alias.st status



### Ignore specific files to be uploaded
To ignore some specific files to be uploaded, you need to make ``.gitignore`` file in the top directory of the repository.  
Ref.: https://git-scm.com/docs/gitignore

