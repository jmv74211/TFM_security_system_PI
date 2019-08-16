#! /bin/bash

####################### LOCATION VARS ###########################

AGENTS_PATH="src/agents"

cd $AGENTS_PATH

function print_parameters {
    echo "Need one of the following parameters"
}

function kill_process {
    PID=`ps -eaf | grep $1 | grep -v grep | awk '{print $2}'`

    if [[ "" !=  "$PID" ]]; then
          echo "- Stopping $1 "
          kill -9 $PID
    else
         echo "- $1 was already stopped"
    fi
}

function check_process {
    PID=`ps -eaf | grep $1 | grep -v grep | awk '{print $2}'`

    if [[ "" !=  "$PID" ]]; then
        echo "- $1 is running"
    else
        echo "- $1 is NOT running"
    fi
}


if [ $# -eq 1 ]; then

    case $1 in

    "start")

        echo "======================================================== \n"
        echo "Starting api agent... \n"
        echo "======================================================== \n"

        python3 api_agent.py > /dev/null 2>&1 & disown

        sleep 3

        echo "======================================================== \n"
        echo "Starting telegram bot... \n"
        echo "======================================================== \n"

        python3 telegram_bot.py > /dev/null 2>&1 & disown

        sleep 2

        echo "======================================================== \n"
        echo "Starting object detector agent... \n"
        echo "======================================================== \n"

        python3 object_detector_agent.py > /dev/null 2>&1 & disown
        ;;

    "stop")

        echo "======================================================== \n"
        echo "Stopping app process... \n"
        echo "======================================================== \n"

        kill_process "object_detector_agent.py"
        kill_process "api_agent.py"
        kill_process "telegram_bot.py"
        ;;

    "status")

         object_detector=`ps -eaf | grep object_detector_agent.py | grep -v grep | awk '{print $2}'`
         api_agent=`ps -eaf | grep api_agent.py | grep -v grep | awk '{print $2}'`
         telegram_bot=`ps -eaf | grep telegram_bot.py | grep -v grep | awk '{print $2}'`

         check_process object_detector_agent.py
         check_process api_agent.py
         check_process telegram_bot.py
        ;;
    *)
        print_parameters
        ;;
    esac

else
    print_parameters
fi

