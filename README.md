virtualenv
======

To avoid the hassle of package dependencies, I use virtualenv to isolate the python environment.

Ensure pip (a package manager for python) is installed, then install virtualenv through pip.

First, type the following code in terminal in the desired directory to create a new virtualenv:

```bash
$virtualenv your_virtualenv_name_of_choice
```

Please DO NOT create the virtualenv inside this repo!

To enter the virtualenv you just created, type:
```bash
$source your_virtualenv_name_of_choice/bin/activate
```
To exit, simple type:

$deactivate

Installing packages through pip
======
After you have enter the virtualenv, change directory to this repo then type the following code to install packages through pip:
```bash
$pip install -r requirements.txt
```

Tornado & Django
======

To start tornado server, type the following command in terminal:
```bash
$python ws.py
```
Tornado will run on port 8080 on default

For Django:
```bash
$python manage.py runserver 0.0.0.0:port (replace port by your desired number)
```
Noted that you must enter the virtualenv first.
