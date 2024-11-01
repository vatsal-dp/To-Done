# Installing To-Done

To-Done is a Django based python webserver meaning there is not too much to do.

## Installation

Please clone the repo onto a suitable system which you would like to run this on.

In the main directory, use the package manager [pip](https://pip.pypa.io/en/stable/) to install the  dependencies using the following command.

```bash
pip install -r requirements.txt
```

## Usage

You will first need to migrate to ensure everything is working properly and the sql database is setup correctly

Use this command to migrate:

```bash
python manage.py migrate
```

Example:

```bash
python manage.py runserver 8080
```

You then just need to go into any web browser and navigate to http://localhost:8080 

Make sure you enable notifications if you would like them and then you should be good to go.
