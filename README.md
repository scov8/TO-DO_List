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

### If you have not already installed ROS & RASA

      sudo bash rasa_ros.sh

1. Install ROS;
2. Install cmake;
3. install RASA.

### Before to run you must run a setup

      sudo bash setup.sh

1. First, install or update SQLite;
2. Check whether an old/obsolete version of Docker is present and if so delete;
3. Download Docker;
4. Take the Duckling container;
5. Launch the project.

### Run to execute the bot

To run the command below, move in the TO-DO_List folder

*_(CHANGE THE CURRENT PSW WITH THE OWN USER PASSWORD)_*

      sudo bash execute.sh

1. Execute: catkin clean, then re-init and build;
2. Execute: source devel/setup.bash;
3. Launch the chatbot with the launch file 'dialogue.xml';
4. Wait the configuration...;
5. Your bot is ready to work. :smile:
