#!/usr/bin/env python3

import inspect
import os
import subprocess
import json
import re
import sys
import paramiko
import h5py
import numpy as np
import time

HOSTNAME = 'sshcampus.ccv.brown.edu'

def get_cell_content(notebook_path, cell_index):
    '''
    This function can be used to retrieve a specific cell
    from a Jupyter notebook.

    Parameters
    ----------
    notebook_path (str): path to the notebook
    cell_index (int): index of the cell to be retrieved

    Returns
    -------
    cell_content (str): the content of the cell
    '''
    with open(notebook_path, 'r') as f:
        data = json.load(f)
    if cell_index < len(data['cells']):
        cell = data['cells'][cell_index]
        if cell['cell_type'] == 'code':
            return ''.join(cell['source'])
        else:
            return "Selected cell is not a code cell"
    else:
        return "Cell index is out of range"

def get_all_fun(the_globals):
    '''
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
    '''
    avoid_funcs = ['open', 'get_all_fun']
    globals_copy = the_globals.copy()
    func_defs = []
    for name, obj in globals_copy.items():
        if (inspect.isfunction(obj) 
            and (name not in avoid_funcs) 
            and ('_' != name[0])):
            try:
                func_def = inspect.getsource(obj)
                func_defs.append(func_def)
            except TypeError:
                print(f"Can't get source code for built-in function {name}.")
    return func_defs

def execute_at_ccv(ccv_cmd, username='jlizaraz'):
    '''
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
    >> long_cmd = \'\'\'
    me="David"
    for i in 1 2 3
    do
        echo "Hello $me."
        echo "$(date)"
    done\'\'\'
    >> oh = execute_at_ccv(long_cmd)
    >> print(oh)
    >>> Hello David.
        Tue Jul 25 17:25:08 EDT 2023
        Hello David.
        Tue Jul 25 17:25:08 EDT 2023
        Hello David.
        Tue Jul 25 17:25:08 EDT 2023
    '''
    # cmd = "ssh jlizaraz@compute_node '%s'" % (HOSTNAME, ccv_cmd)
    cmd = "ssh %s@%s '%s'" % (username, HOSTNAME, ccv_cmd)
    process = subprocess.Popen(cmd, shell=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        # An error occurred
        raise Exception(stderr.decode())
    else:
        # Return command output
        stdo = stdout.decode()
        return stdo

def upload_to_ccv(filename, folder, username='jlizaraz', transferhost = HOSTNAME, verbose=False):
    '''
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
    
    '''
    root_name = os.path.split(filename)[-1]
    command = """
    echo put \"\\\"%s\\\"\" \\\"\"%s/%s\\\"\" | sftp %s@%s
    """ % (filename, folder, root_name, username, transferhost)
    if verbose:
        print(command)
    process = subprocess.Popen(command, 
                               shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    # Wait for the command to complete
    stdout, stderr = process.communicate()

    if verbose:
        # Print the output or the error message, if any
        if process.returncode == 0:
            print(f'Success:\n{stdout.decode()}')
        else:
            print(f'Error:\n{stderr.decode()}')
    return None

def execute_shell_command(ssh_shell, command):
    '''
    Convenience function to execute shell commands at CCV.

    Parameters
    ----------
    ssh_shell (paramiko.Channel): a shell channel to CCV
    command (str): the command as one would type it at the shell

    Returns
    -------
    output (str): the output of the command, as one would see it
    at the shell
    '''
    ssh_shell.send(command + '\n')
    output = ''
    while True:
        while not ssh_shell.recv_ready():
            pass
        data = ssh_shell.recv(4096).decode()
        output += data
        if output.endswith('$ '):
            break
    return output


def run_at_ccv(job_config, verbose=False, closeSSH=False):
    '''
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

    '''
    numCores = job_config['numCores']
    theglobals = job_config['theglobals']
    del job_config['theglobals']
    numJobs  = job_config['numJobs']
    memInGB  = job_config['memInGB']
    username = job_config['username']
    job_name = job_config['job_name']
    importblock = job_config['import_block']
    extra_py = job_config['extra_py']
    special_func = job_config['fun_name']
    funs = get_all_fun(theglobals)
    fire_bit = '''
def main():
    fire.Fire(%s)
if __name__ == '__main__':
    main()''' % special_func

    data_dir = '/users/%s/data/%s/%s' % (username, username, job_name)
    scratch_dir = '/users/%s/scratch/%s' % (username, job_name)
    job_config['data_dir_at_CCV'] = data_dir
    job_config['scratch_dir_at_CCV'] = scratch_dir
    home_dir = os.path.expanduser('~')
    data_dir_at_mac = os.path.join(home_dir, 'ccv', 'data', job_name)
    scratch_dir_at_mac = os.path.join(home_dir, 'ccv', 'scratch', job_name)
    job_config['data_dir_at_mac'] = data_dir_at_mac
    job_config['scratch_dir_at_mac'] = scratch_dir_at_mac

    zzbar_dict = {'data_dir':data_dir, 'scratch_dir':scratch_dir}
    zzbars = []
    for k, v in zzbar_dict.items():
        if isinstance(v, str):
            zzbars.append('%s = \'%s\'' % (k,v))
        else:
            zzbars.append('%s = %s' % (k,v))
    zzvars = '\n'.join(zzbars)
    pieces = [importblock] + [zzvars] + funs + [fire_bit]
    script_text = '\n\n'.join(pieces)
    job_config['script_text'] = script_text

    print("Establishing an SSH connection to CCV and launching a shell ...")
    ccv_ssh = paramiko.SSHClient()
    ccv_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ccv_ssh.connect(HOSTNAME, username=username)
    ssh_shell = ccv_ssh.invoke_shell()

    # make sure that the relevant folders are created at CCV
    for dirname in [data_dir, scratch_dir]:
        execute_shell_command(ssh_shell, 'mkdir %s' % dirname)

    # upload the code
    print("Saving Python script to file ...")
    with open(job_name + '.py', 'w') as f:
        f.write(script_text)
    # upload the script to CCV
    print("Uploading script to CCV ...")
    upload_to_ccv(job_name+'.py', data_dir, verbose=verbose)

    if len(extra_py) > 0:
        for extrap in extra_py:
            if '.py' not in extrap:
                extrap = extrap + '.py'
            upload_to_ccv(extrap, data_dir)

    print("Composing the sbatch script ...")

    sbatch = '''#!/bin/bash
#SBATCH -n {numCores}
#SBATCH --mem={memInGB}GB
#SBATCH -t 1:00:00
#SBATCH --array=0-{numJobs}

#SBATCH -o {job_name}-%a.out
#SBATCH -e {job_name}-%a.out

cd {data_dir}
~/anaconda/foundation/bin/python {data_dir}/{job_name}.py $SLURM_ARRAY_TASK_ID

'''.format(numCores=numCores,
    numJobs = numJobs - 1,
    data_dir = data_dir,
    memInGB = memInGB,
    job_name = job_name
    )
    job_config['sbatch'] = sbatch
    sbatch_fname = '%s-batch.sh' % job_name
    print("Writing sbatch script ...")
    open(sbatch_fname,'w').write(sbatch)
    print("Sending sbatch script ...")
    upload_to_ccv(sbatch_fname, data_dir)
    ccv_sbatch_cmds = ['module load anaconda/3-5.2.0',
    'conda activate foundation',
    'cd',
    'cd %s' % data_dir,
    'sbatch ' + sbatch_fname]
    job_config['ccv_sbatch_cmds'] = ccv_sbatch_cmds
    outputs = [execute_shell_command(ssh_shell, cmd) for cmd in ccv_sbatch_cmds]
    job_config['ccv_sbatch_cmd_outputs'] = outputs
    if verbose:
        print('\n'.join(outputs))
    if closeSSH:
        ssh_shell.close()
        ccv_ssh.close()
        ccv_ssh = None
    return job_config

def execute_command(cmd):
    '''
    Execute a command in the local machine and return its output.

    Parameters
    ----------
    cmd (str): a command, just like one would type on a terminal.

    Returns
    -------
    stdout (str): the standard output of the command.
    '''
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        # An error occurred
        raise Exception(stderr.decode())
    else:
        # Return command output
        return stdout.decode()

def myq():
    '''
    Returns the output of running the myq command at CCV.

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    qu = execute_at_ccv('myq')
    qu = re.sub(r'\n\s*\n', '\n', qu)
    return qu

def pull_from_ccv_to_mac(ccv_folder, mac_folder):
    '''
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
    '''
    if not os.path.exists(mac_folder):
        print("Mac folder does not exist, creating ...")
        os.mkdir(mac_folder)
    if mac_folder[-1] != '/':
        mac_folder += '/'
    if ccv_folder[-1] != '/':
        ccv_folder += '/'
    rsync_cmd = 'rsync -avz jlizaraz@sshcampus.ccv.brown.edu:{ccv_folder} {mac_folder}'.format(ccv_folder=ccv_folder, mac_folder=mac_folder)
    rsync_out = execute_command(rsync_cmd)
    return rsync_out

def load_h5_data(fnames):
    '''
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
    '''
    outs = {}
    for fname in fnames:
        with h5py.File(fname, 'r') as f:
            the_index = int(fname.split('/')[-1].split('.')[0])
            the_params = tuple(np.array(f['in']))
            outs[the_params] = np.array(f['out'])
    out_fun = lambda *params: outs.get(tuple(params), None)
    out_fun.input_params = list(outs.keys())
    return out_fun

def get_ccv_values(mac_folder, ccv_folder, numJobs):
    '''
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
    '''
    out_fnames = []
    wait_time = 1
    num_done = 0
    while len(out_fnames) < numJobs:
        pull_from_ccv_to_mac(ccv_folder, mac_folder)
        out_fnames = os.listdir(mac_folder)
        out_fnames = list(filter(lambda x: x.endswith('.h5'), out_fnames))
        # escalate the waiting time if subsequent checks show no progress
        if num_done == len(out_fnames):
            wait_time += 2
        num_done = len(out_fnames)
        # print('Waiting for %d jobs to finish' % (numJobs - num_done))
        progress_bar(num_done, numJobs, prefix = 'Progress:', suffix = 'Complete', length = 30)
        time.sleep(1)
    out_fnames = [os.path.join(mac_folder, fname) for fname in out_fnames]
    out_fun = load_h5_data(out_fnames)
    return out_fun

def progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 50, fill = '█'):
    '''
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
    '''
    # Calculate elapsed time and estimated remaining time
    global start_time
    if iteration == 0:
        start_time = time.time()
    elapsed_time = time.time() - start_time
    remaining_time = (elapsed_time * (total / (iteration + 1))) - elapsed_time if iteration > 0 else 0

    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix} Elapsed Time: {elapsed_time:.2f}s Remaining Time: {remaining_time:.2f}s', end = '\r')
    sys.stdout.flush()  # add this line
    # Print New Line on Complete
    if iteration == total: 
        print()