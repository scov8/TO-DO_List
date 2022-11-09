# TO-DO List Group 8

■ Develop a ROS dialogue systems that allows the user to insert and remove activities from a to-do lists. The dialogue system also needs to allow the user to activate a reminder when the deadline is approaching.

■ Each element in the list is identified by a tag (identifying the activity), a deadline and a category (es: CR course, sport, personal etc) (\*).

■ The dialogue systems must allow the user to:

- Look the activities in the to do list
- Insert a new activity in the to do list
- Remove an activity from the to do list

■ OPTIONAL features:

- Manage multiple users
- (\*) Manage multiple categories of to do list
- Update an activity in the to do list

# HOW TO RUN
In order to launch the project, there are a number of steps to be taken.<br />
We provide a **_setup.bash_** with which the packages of interest concerning **SQLite** and **Duckling** are installed.
We use SQLite to store all the information about tasks and users, meanwhile Duckling is an extractor used for date and time.<br />
For convenience, we use the duckling container on **Docker**; once downloaded via setup.bash, and launched the project, Duckling will start automatically.
<br />
### Steps of the setup.bash:
1. First, install or update SQLite;
2. Check whether an old/obsolete version of Docker is present and if so delete;
3. Download Docker;
4. Take the Duckling container.
