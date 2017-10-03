# shiny-eureka
Cloud Computing Assignment 1

A simple picture blog website

# Get Started

## Virtual environment setup

Firstly you need to create a virtual environment with python 3.5 and activate this environment
```
virtualenv -p python3 envname
sudo source path_to_envname/bin/activate
```
Then install the packages listed in the requirement file.
```
pip install -r requirements.txt
```

## Setup the configuration

Please change the sensitive information like the secret key, configuration for database in development.py or production.py wihtin the instance folder.

By default, the start.sh uses development.py as the configuration and you can change it if you want.

To start the app, input the code below in the root directory.
```
./start.sh
```

# Screenshot
![](http://owatmapyv.bkt.gdipper.com/Home%20Photo%20Library.png)
![](http://owatmapyv.bkt.gdipper.com/Home%20Photo%20Library%20amplify.png)
