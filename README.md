# Expense Tracking Project

## Set Up Machine
I am working on a Linux machine with Ubuntu 20.04.
Type ` lsb_release -a` to check your version.  My results are:

```
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 20.04.3 LTS
Release:	20.04
Codename:	focal
```

### Install required packages

You need to install the following packages, if they are not already installed:
1. Update system: Type `sudo apt-get update`
2. Upgrade system: Type `sudo apt-get upgrade`
3. Python3: Type `sudo apt-get upgrade python3`
4. Pip3: Type `sudo apt install -y python3-pip`
5. Virtualenv: Type `sudo apt-get install python3-venv`
6. PostgreSQL: Type `sudo apt install postgresql postgresql-contrib`
7. Git: Type `sudo apt install git-all`

### Set up PostgreSQL Database

1. Make sure postgreSQL service is running: Type `sudo service postgresql start`
2. Access postgreSQL: Type `sudo -u postgres psql postgres`
3. Set the password: Type `\password <password>` (for postgres; NOT user's password for new db)
4. Create database: Type `CREATE DATABASE <database name>;`
5. Connect to database: Type `\c <database name>`
6. Create a user: Type `CREATE USER <user> WITH PASSWORD '<user password>';`
7. Set encoding: Type `ALTER ROLE <user> SET client_encoding TO 'utf8';`
8. Set default transaction: Type `ALTER ROLE <user> SET default_transaction_isolation TO 'read committed';`
9. Set timezone: Type `ALTER ROLE <user> SET timezone TO 'EST';`
10. Grant permissions: Type `GRANT ALL PRIVILEGES ON DATABASE <database name> TO <username>;`
11. Exit PostgreSQL: Type `\q`

### Set Up Project Directory

1. Type `mkdir django-expense` or any name for the directory you choose
2. Change into the newly created directory: Type `cd django-expense`
3. Type `python3 -m venv expense-venv` to create virtural environment
4. Activate virtual environment: Type `source expense-venv/bin/activate`
   NOTE:  Your will see `(expense-venv)` before your prompt
5. Clone this repository: Type `git clone https://github.com/MKing301/expenses.git`
6. Change into repository directory: Type `cd expenses`
7. Install required packages: Type `pip install -r requirements.txt`
8. Create environment variables file: Type `touch .env`
9. Add environment variables: Type `nano .env`
   NOTE: You can use your favorite text editor if you prefer, instead of nano

   a. Add the following lines to the .env files

   ```
   # Secret Key
   export SECRET_KEY="your secret key here"

   # Postgresql Database
   export DB_NAME="your database from above name here"
   export DB_USER="your database user name from above here"
   export DB_USER_PASSWORD="your database user password from above here"
   ```

   b. If using nano, type `CTRL + O` then `ENTER` to save, then `CTRL + X` to exit nano

### Verify Django Development Server Working

1. Type `python manage.py runserver`

You should see the following:

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 02, 2022 - 21:35:23
Django version 4.0.2, using settings 'project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

2. Open your browser and enter `http://127.0.0.1:8000/`

You should see **The installion worked successfully! Congratulations!** in the middle of the screen.

### MORE TO COME SOON !!!
