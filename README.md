# Catalog-App

## I.Design of Code
#### Description of the project
This catalog application provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items. This web application deployes the Python framework _Flask_ together with using third-party OAuth authentication via Google's authentication services.

#### Database
The _categoryitems_ database contains three tables as follows:
  1. Table **user** with columns *id*, *name*, *email*, *picture*:
    - Primary key: *id*, referenced by Table **category**(*user_id*).
  2. Table **category** with columns *id*, *name*, *user_id*, *user*:
    - Primary key: *id*;
    - Foreign key: *user_id*, references Table **user**(*id*).
  3. Table **item** with columns *id*, *name*, *description*, *category_id*, *category*,*user_id*, *user*:
    - Primary key: *id*;
    - Foreign key: *user_id*, references Table **user**(*id*); *category_id*, references Table **category**(*id*).
   
   
## II. Run the Code
#### Step 1: DOWNLOAD
  - Download and install [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads) on your computer.
  - Download and install [the Vafrantfile](https://github.com/yiyupan/fullstack-nanodegree-vm), where _news_ database has been already set.
  - Download all the files in this repository and move those files into `vagrant` directory which is shared with your virtual machine.
#### Step 2: LOG INTO VIRTUAL MACHINE
Open up the `vagrant` directory. To use the command `vagrant up` to bring the virtual machine back online, and log into it with `vagrant ssh`.
#### Step 3: LOAD DATABASE
Access to shared files by using the command `cd \vagrant`.
Use the command `python database_setup.py` to setup database and use the command `python lotsofitems.py` to load default categories and items.
#### Step 4: START SERVER
Use the command `python application.py` to run the application server.
#### Step 5: OPEN WEBSITE
Open up your web browser, visit `http://localhost:8000` or `http://localhost:8000/catalog/`. You can add new items and also edit, delete  your own items after logging in.
