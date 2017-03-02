#<a name="top"></a>FIWARE TSC Enablers Dashboard
[![License badge](https://img.shields.io/badge/license-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Scripts to generate the Enablers Dashboard to evaluate the use of the different components.

These scripts were developed in order to facilitate the activities in the FIWARE Technical Steering
Committee. The purpose is generate automatically a google excel file in which we show the use of
the differents Generic Enablers that are available in FIWARE.

These scripts were originally develop by Manuel Escriche from Telefónica I+D and now 
is maintained by me. I just try to cover python style reorganize content to separate 
the scripts and generate a separate project for it. Eventually, I generate a proper project to allow
the continue execution of the component every day and describe how to install the component.

## Build and Install

### Requirements

The following software must be installed:

- Python 2.7
- pip
- virtualenv


### Installation

The recommend installation method is using a virtualenv. Actually, the installation 
process is only about the python dependencies, because the python code do not need 
installation.

1. Clone this repository.
2. Define the configuration file in './config/tsc-dashboard.ini'
3. Create your Google Credential in the './config/dashboard-credential.json' file.
4. Create your Google service account key in the './config' directory
5. Define owners.json file in the './config' directory.
6. Execute the script 'source config.sh'. 
7. With root user, execute the command 'cp ./config/tsc-dashboard.logrotate /etc/logrotate.d/tsc-dashboard

This script (config.sh) will execute the configuration of the python virtualenv and 
modify the file 'dashboard.py' in order to allow the automatic execution of the 
python file. 

Please, take a look to the https://console.developers.google.com in order to know more details 
about the configuration of the credential for your application. Now the system is ready to use. 
You do not need to activate the virtualenv. The scripts will do it for you.

[Top](#top)

### Configuration

The script is searching the configuration parameters or in the '/etc/fiware.d'
directory or in the environment variables. Firstly, The script try to find if there 
is defined an environment variable whose name is 'TSC_DASHBOARD_SETTINGS_FILE'. 
If the script cannot get this environment variable, it tries to find the file 
'tsc-dashboard.ini' in '/etc/init.d' directory. In any oder case or the file does 
not exist, the scripts will give you an error.

## Run

To execute the scripts, you only need to execute the following command:

$ ./dashboard.py --noauth_local_webserver

The first time that you execute it, you will be requested to provide access and write
a verification code for your application. The following ones, you do not need to 
repeat this process again.

Keep in mind that the config.sh script modify the crontab file, therefore the application
will be executed every working day at 4 o'clock.

[Top](#top)

## License

These scripts are licensed under Apache License 2.0.
