<p align="center">
  <img src="img/todone-logo.png" />
</p>
<h2 align="center">The Only Todo List You Need</h2>

[![Coverage Status](https://coveralls.io/repos/github/CSC510-Team-57/To-Done/badge.svg?branch=main)](https://coveralls.io/github/CSC510-Team-57/To-Done?branch=main)
[![Pylint Score](https://byob.yarr.is/CSC510-Team-57/To-Done/pylint_score)](https://github.com/CSC510-Team-57/To-Done/actions)
[![license badge](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/CSC510-Team-57/To-Done/blob/main/LICENSE)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Django 4.1](https://img.shields.io/badge/django-4.1-blue.svg)](https://docs.djangoproject.com/en/4.1/releases/4.1/)
[![DOI](https://zenodo.org/badge/878680678.svg)](https://doi.org/10.5281/zenodo.14016079)


# TO-DONE

`to-done` lets you manage your todo list effectively with minimal effort. With a minimalistic web interface, 
you can access your todolist on the go. Use our rich library of templates to create a new todo list very fast or create your own.

### Watch this video to know more about TO-DONE 2.0


https://user-images.githubusercontent.com/23623764/205810552-556e0449-3f81-4e55-ad9a-414de9731b15.mp4


### Watch this video to know more about the original TO-DONE 
<img src="img/todone-create-list.gif" width="1200" height="500" />

Contents
========

 * [Why?](#why)
 * [Features](#key-features-last-version)
 * [New Features](#new-features)
 * [Upcoming Features](#upcoming-features)
 * [Quick Start](#quick-start)
 * [Documentation](#Documentation)
 * [Want to contribute?](#want-to-contribute)
 * [License](#license)
 * [Developer](#developers-new-version)

### Why?

We wanted to work on something that is:

+ Useful, serves some real purpose
+ Easy to start with a basic working version and lends itself to adding new features incrementally to it
+ Easily divisible in modules/features/tasks that can be parallely done by five developers 
+ Diverse enough so that a lot of Software Engineering practices is required/involved 

`to-done` is a todo list app that is actually useful, very easy to create a basic working version with where a ton of new features can be added, touches upon all the aspects of web programming, database, working in a team etc.

### Key Features (Previous Versions Version)
 * [Register](#register)
 * [Login](#login-forget-password)
 * [Create, Update, Delete Todo Lists](#manage-todo-list)
 * [Quickly Create Todo Lists From Existing Templates](#templates)
 * [Create Your Own Templates](#templates)
 * [Shared List](#shared-todo-lists)
 * [Add Due Date To Tasks](#due-date-color-tags)
 * [Due Date Alerting Mechanism](#due-date-color-tags)
 * [Add Reminder Message to task completed](#due-date-color-tags)
 * [Customized Color Tag](#due-date-color-tags)
 * [Add Tags To Todo Lists For Customizable Grouping](#customizable-grouping-tags)

### New Features
 * [Notifications]
 * [On-time metrics]
 * [Tasks sorted by due date]
 * [Dark Mode]
 * [Default templates]
 * [Priority Tracker]

### Upcoming Features
 * Social login
 * Export and import to-do lists
 * Gamification - earn points by finishing your tasks, show-off your productivity in social media
 * [List of All Planned Features for Second Phase](https://github.com/users/shahleon/projects/2/views/6)

### Quick Start

 * [Download](https://www.python.org/downloads/release/python-380/) and install Python 3.8.0 or higher
 * [Install](https://docs.djangoproject.com/en/4.1/topics/install/) Django 4.1
 * Clone the repository
    ```bash
    $ git clone git@github.com:Chloe-Ku/smart-todo.git
    ```
 * Run migrations
    ```bash
    $ python manage.py migrate
    ```
 * Start the app
    ```bash
    $ python manage.py runserver 8080
    ```
 * Point your browser at http://127.0.0.1:8080 and explore the app

### Documentation
[See this page](https://chloe-ku.github.io/smart-todo/)

### Features

#### Register
<p float="middle">
    <img src="img/todone-register.gif" width="500" height="250" />
</p>

#### Login, Forget Password
<p float="middle">
    <img src="img/todone-login.gif" width="500" height="250" /> 
</p>

#### Manage Todo List
<p float="middle">
    <img src="img/todone-create-list.gif" width="500" height="250" />
    <br>
    <br>
    <img src="img/todone-update-list.gif" width="500" height="250" />
</p>

#### Templates
<p float="middle">
    <img src="img/todone-templates.gif" width="500" height="250" />
</p>

### New Features
#### Customizable Grouping Tags
<p float="middle">
    <img src="img/todone-tag-list.gif" width="500" height="250" />
</p>

#### Shared ToDo Lists
<p float="middle">
    <img src="img/todone-shared-list.gif" width="500" height="250" />
</p>

#### Due Date, Color Tags
<p float="middle">
    <img src="img/todone-tag-color.gif" width="500" height="250" />
</p>


### Want to Contribute?

Want to contribute to this project? Learn about [Contributing](CONTRIBUTING.md). Not sure where to start? Have a look at 
the [good first issue](https://github.com/shahleon/smart-todo/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22). Found a bug or have a new feature idea? Please create an [Issue](https://github.com/Chloe-Ku/smart-todo/issues) to notify us.

### License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

### Developers (New Version)

<table>
  <tr>
    <td align="center"><a href="https://github.com/Charlie-Eastin"><img src="https://avatars.githubusercontent.com/u/176774701?s=400?v=4" width="100px;" alt=""/><br /><sub><b>Charlie Eastin</b></sub></a></td>
    <td align="center"><a href="https://github.com/SpencerKersey"><img src="https://avatars.githubusercontent.com/u/77792710?v=4" width="100px;" alt=""/><br /><sub><b>Spencer Kerseyb></sub></a><br /></td>
    <td align="center"><a href="https://github.com/Shawty2084"><img src="https://avatars.githubusercontent.com/u/89483146?v=4" width="100px;" alt=""/><br /><sub><b>Aastha Gaudani</b></sub></a><br /></td>
  </tr>
</table>

### Developers (Last Version)

* Shahnewaz Leon (sleon3@ncsu.edu)
* Dong Li (dli35@ncsu.edu)
* Cheng-Yun Kuo (ckuo3@ncsu.edu)
* Drew Commings (docummin@ncsu.edu)
* Janet Brock (jdbrock@ncsu.edu)
* Chiu, Ching-Lun
* Yu, Hsueh-Yang
* Lin, Po-Hsun
* Ku, Li-Ling
* Chiang, Chen-Hsuan
