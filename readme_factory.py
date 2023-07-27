#!/usr/bin/env python3

import os
import ast

readme_header = '''# zizibee 

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

'''

excluding = ['reboot.py']

def extract_function_data(node):
    """Extract the function name, parameters and docstring."""
    name = node.name
    params = [arg.arg for arg in node.args.args]
    docstring = ast.get_docstring(node)
    
    return name, params, docstring

def extract_from_source(source):
    """Extract function data from the source code."""
    tree = ast.parse(source)
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    function_data = {extract_function_data(f)[0]: {"params": extract_function_data(f)[1], "docstring": extract_function_data(f)[2]} for f in functions}

    return function_data

def extract_from_directory(directory, exclude=[]):
    """Extract function data from all .py files in a directory."""
    function_data = {}
    
    for filename in os.listdir(directory):
        if filename.endswith('.py') and (filename not in exclude):
            with open(os.path.join(directory, filename), 'r') as f:
                source = f.read()
                function_data[filename] = extract_from_source(source)
    
    return function_data

def format_markdown(function_data):
    """Formats the function data as markdown."""
    markdown = ""
    
    for file, functions in function_data.items():
        markdown += f"## File: {file}\n"
        
        for name, data in functions.items():
            markdown += f"### {name}({',  '.join(data['params'])})\n"
            if data['docstring']:
                markdown += f"```Docstring:\n{data['docstring']}\n```\n"
            else:
                markdown += ""
    
    return markdown

def main():
    directory = os.getcwd()
    function_data = extract_from_directory(directory, exclude=excluding)
    markdown = format_markdown(function_data)
    readme_bits = [readme_header, markdown]
    readme = "\n".join(readme_bits)
    with open("README.md", "w") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
