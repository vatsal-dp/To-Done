x<p align="center">
  <img src="img/todone-logo.png" />
</p>
<h2 align="center">The Only Todo List You Need</h2>

[![Coverage Status](https://coveralls.io/repos/github/vatsal-dp/To-Done/badge.svg?branch=vatsal)](https://coveralls.io/github/vatsal-dp/To-Done?branch=vatsal)
[![Pylint Score](https://byob.yarr.is/CSC510-Team-57/To-Done/pylint_score)]([https://github.com/vatsal-dp/To-Done/actions/workflows/pylint.yml])
[![license badge](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/CSC510-Team-57/To-Done/blob/main/LICENSE)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Django 4.1](https://img.shields.io/badge/django-4.1-blue.svg)](https://docs.djangoproject.com/en/4.1/releases/4.1/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.14226147.svg)](https://doi.org/10.5281/zenodo.14226147)

# TO-DONE

`to-done` lets you manage your todo list effectively with minimal effort. With a minimalistic web interface,
you can access your todolist on the go. Use our rich library of templates to create a new todo list very fast or create your own.

### Watch this video to know more about TO-DONE 4.0

https://github.com/user-attachments/assets/85536889-977e-4303-90bf-854530edb9c9

### DEMO

https://github.com/user-attachments/assets/3c9f46e8-8f61-40e0-966f-41128f4c75d9

# Contents

- [Why?](#why)
- [Features](#key-features-last-version)
- [New Features](#new-features)
- [Upcoming Features](#upcoming-features)
- [Quick Start](#quick-start)
- [Documentation](#Documentation)
- [Want to contribute?](#want-to-contribute)
- [License](#license)
- [Developer](#developers-new-version)

### Why?

We wanted to work on something that is:

- Useful, serves some real purpose
- Easy to start with a basic working version and lends itself to adding new features incrementally to it
- Easily divisible in modules/features/tasks that can be parallely done by five developers
- Diverse enough so that a lot of Software Engineering practices is required/involved

`to-done` is a todo list app that is actually useful, very easy to create a basic working version with where a ton of new features can be added, touches upon all the aspects of web programming, database, working in a team etc.

### Key Features (Previous Versions Version)

- [Register](#register)
- [Login](#login-forget-password)
- [Create, Update, Delete Todo Lists](#manage-todo-list)
- [Quickly Create Todo Lists From Existing Templates](#templates)
- [Create Your Own Templates](#templates)
- [Shared List](#shared-todo-lists)
- [Add Due Date To Tasks](#due-date-color-tags)
- [Due Date Alerting Mechanism](#due-date-color-tags)
- [Add Reminder Message to task completed](#due-date-color-tags)
- [Customized Color Tag](#due-date-color-tags)
- [Add Tags To Todo Lists For Customizable Grouping](#customizable-grouping-tags)
- [Notifications](#notifications)
- [On-time metrics](#on-time-metrics)
- [Tasks sorted by due date](#tasks-sorted-by-due-date)
- [Dark Mode](#dark-mode)
- [Priority Tracker](#priority)

### New Features

- [Fixed Daylight saving time](#fixed-daylight-saving-time)
- [Email Notification](#email-notification)
- [Add list in Google Calendar](#add-list-in-google-calendar)
- [Shared Lists](#shared-list)
- [UI Improvements](#ui-improvements)

### Upcoming Features

- Containerization
- User Authentication via OTP
- Progress Tracking
- Mobile App Browser Extension

### Quick Start

- [Download](https://www.python.org/downloads/release/python-380/) and install Python 3.8.0 or higher
- [Install](https://docs.djangoproject.com/en/4.1/topics/install/) Django 4.1
- Clone the repository
  ```bash
   https://github.com/vatsal-dp/To-Done.git
  ```
- Update migrations
  ```bash
   python manage.py makemigrations
  ```
- Run migrations
  ```bash
   python manage.py migrate
  ```
- Start the app
  ```bash
   python manage.py runserver 8000
  ```
- Point your browser at localhost:8000 and explore the app

### Documentation

[See this page](https://chloe-ku.github.io/smart-todo/)


### Want to Contribute?

Want to contribute to this project? Learn about [Contributing](CONTRIBUTING.md). Found a bug or have a new feature idea? Please create an [Issue](https://github.com/CSC510-Team-57/To-Done/issues) to notify us.

### License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

### Developers (New Version)

<table>
  <tr>
    <td align="center"><a href="https://github.com/vatsal-dp"><img src="https://avatars.githubusercontent.com/u/75309827?v=4" width="100px;" alt=""/><br /><sub><b>Vatsal Patel</b></sub></a></td>
    <td align="center"><a href="https://github.com/smitraval24"><img src="https://avatars.githubusercontent.com/u/121729070?v=4" width="100px;" alt=""/><br /><sub><b>Smit Raval</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/devyash2930"><img src="https://avatars.githubusercontent.com/u/74496621?v=4" width="100px;" alt=""/><br /><sub><b>Devyash Shah</b></sub></a><br /></td>
  </tr>
</table>

### Developers (Last Version)
- Aastha Gaudani
- Spencer Kerseyb
- Charlie Eastin
- Shahnewaz Leon (sleon3@ncsu.edu)
- Dong Li (dli35@ncsu.edu)
- Cheng-Yun Kuo (ckuo3@ncsu.edu)
- Drew Commings (docummin@ncsu.edu)
- Janet Brock (jdbrock@ncsu.edu)
- Chiu, Ching-Lun
- Yu, Hsueh-Yang
- Lin, Po-Hsun
- Ku, Li-Ling
- Chiang, Chen-Hsuan
