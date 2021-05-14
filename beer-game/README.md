### Beer Distribution Game

This is a simple supply chain management simulation game using Django.

### Project Structure

# Setup Guide

1. Clone this repository

2. Install **MySQl** (if not currently installed)
3. Create a virtual environment and activate it. More information regarding that can be found [here](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/)
4. All the dependencies of this project can be found in requirements.txt file. In order to install them just run the command:

```
pip install -r requirements.txt
```

If one of the dependencies cannot be installed, try to install them with pip.\
Note: More information installing **mysql-client** (Windows/Linux) if the above command did not work can be found [here](https://medium.com/@omaraamir19966/connect-django-with-mysql-database-f946d0f6f9e3).

5. After installation create a new database on Mysql, and include the information regarding it in /mysite/settings.py in the DATABASES section. More information can be found in the link given above.

6. Make migrations (construction of the database)

```
python manage.py makemigrations
python manage.py migrate

```

7. Run the server

```
python manage.py runserver

```

8. Navigate to http://localhost:8000/ and enjoy the game!

For a better testing of the game:

- Create 5 users (4 students, 1 instructor), signup, login
- Login in with the instructor and create some games (more than 1), including the students you created, having different options (wholesaler, distributor present/not present). Recommended: Nr of weeks should not be too large, and information delay should be small (to notice the game logic better)
- Start the games, at the main page, by clicking the link start game.
- For testing purposes, each round lasts only 5 minutes. These can be changed at /views/crudGame.py. You have a variable at top, called round*length. If you want hours, days,weeks, instead of minutes you can change that at \_startGame* view found in the same file.
- Login in with the users created and play all the games concurrently. Do that for all the users (keep in mind the 5 minute length of the round).
- You can notice that the logic of the game is implemented (order placed by a role, becomes a demand to another one, outgoing shipment becomes incoming shipment to the other role of the same game)
- You can view the plots, the tables, or monitor the game (through the admin of the game).

# Testing

After doing the steps described in setup, the application can be tested with the command (in the root directory):

```
python manage.py test game
```
