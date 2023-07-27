# zizibee 

<img src="./img/zizibees.png" alt="zizibees" width="200"/>

`zizibee` is a set of tools useful to schedule and manage jobs at a cluster. Many things would probably only work on a Unix-line machine since some tasks depend on stringing together command-line tools.

It solves the problem of having to copy and paste code from a notebook to a .py file to be able to run it at CCV. It does this by finding the functions that have been defined in the running notebook, and puts them together with other requirements in a single .py file that is then uploaded to CCV using sftp.

For this to work one needs to be either on campus, or connected through the VPN.

It assumes that there's a function that needs to be executed in an enumerated set of parameters. To provide these input values to the function of interest a necessary helper function needs to be defined. This function takes an integer and returns a tuple with the corresponding parameters.

The output of the function can be a numpy array of arbitrary shape, and should be saved to disk in an .h5 file.

For giving the function of interest a command-line interface, which is useful when setting up the sbatch shell script, `zizibee` uses [fire](https://github.com/google/python-fire).

To execute some of the remote commands necessary to set this up, `zizibee` establishes an SSH connection to CCV using [paramiko](https://www.paramiko.org).

As an additional convenience `zizibee` also provides a convenience function that uses rsync to pull all the files from a remote directory at CCV. Once all expected number of files have been collected, it creates a function that allows getting the values computed at CCV.

Most of this assumes that passwordless SSH login to CCV has been already configured.

In addition to this, this repository also provides the following:

* `readmy_factory.py`: useful to create a markdown file with the docstrings of all the functions defined in a directory. This is useful to create a README.md file for a repository.
* `ccv_stats.py`: useful to get a list of the users currently using OSCAR and how many cores they are using. It can also produce a graph of this information.
* `multitester.py`: useful to compare the multi-core performance of different machines and configs. It runs a sequence of common tasks using numpy and sympy.
* `tester.py`: useful to test the performance of a machine by running a sequence of common tasks using numpy and sympy.


## File: tester.py
### fft()
### eig()
### rando()
### multi()
### matinv()
### sorter()
### itersum()
### funceval()
### symbexpand()
### benchman(repeats)
```Docstring:
Standard score is 1000, which is performance of 2021 MacBook Pro 16".
```
## File: zizibee.py
### get_cell_content(notebook_path,  cell_index)
```Docstring:
This function can be used to retrieve a specific cell
from a Jupyter notebook.

Parameters
----------
notebook_path (str): path to the notebook
cell_index (int): index of the cell to be retrieved

Returns
-------
cell_content (str): the content of the cell
```
### get_all_fun(the_globals)
```Docstring:
This   function   receives  a  dictionary  with  the  global
variables and returns a list with the definitions of all the
functions defined in the given namespace.

Parameters
----------
the_globals   (dict):   the   dictionary   with  the  global
variables, usually this is is simply the output of globals()
but  it  needs  to be given explicitly because otherwise the
function would be using its own globals().

Returns
-------
func_defs  (list): a list with the definitions the functions
defined in the_globals.
```
### execute_at_ccv(ccv_cmd,  username)
```Docstring:
Execute  a command at CCV and return its output. The command
can  be  multiline  and  include  many  statements.  This is
accomplished by using the ssh command to execute the command
at CCV. This is done through a login mode (although it could
be  modified) so in its present form it should't be used for
resource-intensive tasks.

Parameters
----------
ccv_cmd (str): a command (or many) to execute at CCV

Returns
-------
stdo (str): the standard output of the sent command.

Example
-------
>> long_cmd = '''
me="David"
for i in 1 2 3
do
    echo "Hello $me."
    echo "$(date)"
done'''
>> oh = execute_at_ccv(long_cmd)
>> print(oh)
>>> Hello David.
    Tue Jul 25 17:25:08 EDT 2023
    Hello David.
    Tue Jul 25 17:25:08 EDT 2023
    Hello David.
    Tue Jul 25 17:25:08 EDT 2023
```
### upload_to_ccv(filename,  folder,  username,  transferhost,  verbose)
```Docstring:
This  function can be used to upload local files to a folder
at CCV.

Parameters
----------
filename  (str):  path  of the file to be uploaded, can be a
full or relative path.
folder (str): file will be uploaded to this folder
username (str): username at CCV
transferhost(str): the hostname of the transfer node at CCV
verbose (bool): whether to print out the command executed to
upload the file

Returns
-------
None
```
### execute_shell_command(ssh_shell,  command)
```Docstring:
Convenience function to execute shell commands at CCV.

Parameters
----------
ssh_shell (paramiko.Channel): a shell channel to CCV
command (str): the command as one would type it at the shell

Returns
-------
output (str): the output of the command, as one would see it
at the shell
```
### run_at_ccv(job_config,  verbose,  closeSSH)
```Docstring:
Send a grid job to CCV.

Parameters
----------
job_config   (dict):   with   at  least  the
following keys:
    > username (str): the username at CCV.
    >   numCores   (int):   how  many  cores
    required for each job.
    >  numJobs  (int):  how  many evaluation
    points will be run.
    >   memInGB   (int):   how  much  memory
    required for each job.
    >  import_block  (str): the import block
    of the script to be run.
    >  extra_py  (list):  list  of  paths to
    extra python files to be uploaded.
    > theglobals (dict): the dictionary with
    the global variables.
    >   fun_name  (str):  the  name  of  the
    function to be run at CCV.
    > job_name (str): the name of the job.
verbose  (bool):  if True some debug mesages
are printed
closeSSH   (bool):  if  True  then  the  SSH
connection and sheel are closed at the end

Returns
-------
job_config   (dict)   with   the   following
additional keys
    > data_dir_at_CCV (str): the path to the
    data folder at CCV
    >  scratch_dir_at_CCV (str): the path to
    the scratch folder at CCV
    > data_dir_at_mac (str): the path to the
    data folder at the mac
    >  scratch_dir_at_mac (str): the path to
    the scratch folder at the mac
    >  sbatch  (str): the text of the sbatch
    script
    >   ccv_sbatch_cmds   (list):  with  the
    commands  that  were executed to run the
    batch job
    >  script_text  (str):  the  text of the
    uploaded script
    >   (theglobals   is  deleted  from  the
    job_config dictionary)
```
### execute_command(cmd)
```Docstring:
Execute a command in the local machine and return its output.

Parameters
----------
cmd (str): a command, just like one would type on a terminal.

Returns
-------
stdout (str): the standard output of the command.
```
### myq()
```Docstring:
Returns the output of running the myq command at CCV.

Parameters
----------
None

Returns
-------
None
```
### pull_from_ccv_to_mac(ccv_folder,  mac_folder)
```Docstring:
All the files from ccv_folder will be synced to mac_folder.
None  of  the changes at the mac_folder will be reflected at
the ccv_folder.

Parameters
----------
ccv_folder (str): path to a folder at CCV
mac_foler  (str): path to a folder at the mac

Returns
-------
rsync_out (str): the stdout of the rsync command
```
### load_h5_data(fnames)
```Docstring:
This  function takes the filenames from a bunch of .h5 files
and  creates  a  function  that  can  be used to explore the
return values for the corresponding inputs.

Parameters
----------
fnames (list): list of paths to the h5 files

Returns
-------
ccv_fun (function): function that takes the input parameters
and  returns the data, this function has an attribute called
keys  that  contains the input parameters that it is defined
for.
```
### get_ccv_values(mac_folder,  ccv_folder,  numJobs)
```Docstring:
This  function  uses  rsync to pull the data from CCV to the
Mac, it does this periodically until all the expected output
files have been downloaded.
Once  these  files  have  been  all retrieved, they are then
loaded into a function that can be used to retrieve the data
with  the  same  call signature as the original function (at
least in shape).
The  returned  function has an attribute called input_params
that  contains  the  input parameters for which the function
was evaluated.
If  an  input  is  given  for  which  the  function  was not
evaluated, then the function returns None.

Parameters
----------
mac_folder  (str): path to the folder where the data will be
downloaded
ccv_folder  (str):  path  to the folder where the data is at
CCV
numJobs (int): how many jobs are expected

Returns
-------
out_fun (function): function that takes the input parameters
and returns the data.
```
### progress_bar(iteration,  total,  prefix,  suffix,  decimals,  length,  fill)
```Docstring:
A convenient progress bar.

Parameters
----------
iteration (int): current iteration
total (int): total iterations
prefix (str): prefix string
suffix (str): suffix string
decimals (int): positive number of decimals in percent complete
length (int): character length of bar
fill (str): bar fill character

Returns
-------
None
```
## File: ccv_stats.py
### oscar_users()
```Docstring:
Get the names of the users currently using OSCAR.

Parameters
----------
None

Returns
-------
(users, cpus) (list, list): with the users and how many cores they are using
```
## File: multitester.py
### poolrun(fun,  reps)
### fft()
```Docstring:
The fast Fourier transform of 100'000 random real numbers.
```
### eig()
```Docstring:
The eigenvalues of a 100x100 random matrix.
```
### rando()
```Docstring:
A 2000x2000 array of random numbers.
```
### multi()
```Docstring:
Matrix multiplication of two 100x100 random matrices.
```
### matinv()
```Docstring:
Matrix inversion of a 100x100 random real matrix.
```
### sorter()
```Docstring:
Sorting 10000 random real numbers.
```
### itersum()
```Docstring:
A for loop running a nested sum over one million iterations.
```
### funceval()
```Docstring:
Function evaluation of some common functions.
```
### symbexpand()
### benchman(repeats)
```Docstring:
Standard score is 1000, which is performance of 2021 MacBook Pro 16".
```
## File: readme_factory.py
### extract_function_data(node)
```Docstring:
Extract the function name, parameters and docstring.
```
### extract_from_source(source)
```Docstring:
Extract function data from the source code.
```
### extract_from_directory(directory,  exclude)
```Docstring:
Extract function data from all .py files in a directory.
```
### format_markdown(function_data)
```Docstring:
Formats the function data as markdown.
```
### main()
