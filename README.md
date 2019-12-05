# WebDB

## Description

This website runs an analysis procedure regarding the US presidential race of 2020, 
specifically regarding the connection between the media coverage of candidates and their
polling results.

This project is inspired by [Nate Silver's fivethirtyeight](fivethirtyeight.com) platform. 

## How to run the project.
### Prerequisites:

* Make sure you have all the Python prerequisites installed:
```bash
$ pip install --user --requirement requirements.txt
```
* Install npm, with your project manager, or from <https://www.npmjs.com/get-npm>. Then install
the npm packages:
```bash
$ npm install
```

### Running: 
The project consists of a Django backend, and a node.js frontend. We will need to run 
both of these services in order to benefit from the full functionality of the platform.
In two separate Terminal windows, do:
```bash
$ npm run start
```
and 
```bash
$ python manage.py runserver
```
