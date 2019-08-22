#! /bin/bash

####################### LOCATION VARS ###########################

OBJECT_DETECTOR_INSTALLED="false"
AGENTS_PATH="src/agents"

cd $AGENTS_PATH

function print_parameters {

    echo -e "Usage: app.sh <arg>"
    echo -e "Common args:"
    echo -e "     start          Launches the necessary processes to start the application"
    echo -e "     stop           Stops all application processes"
    echo -e "     status         Displays the status of application processes"

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

        echo "========================================================"
        echo "Starting api agent agent worker..."
        echo "========================================================"

        celery -A api_agent.celery worker -n api_agent -l INFO -c 1 -Q api_agent > /dev/null 2>&1 & disown

        sleep 2

        if [[ $OBJECT_DETECTOR_INSTALLED ==  "true" ]]; then

            echo "========================================================"
            echo "Starting celery motion agent worker..."
            echo "========================================================"

            celery -A motion_agent.celery worker -n motion_agent -l INFO -c 1 -Q motion_agent > /dev/null 2>&1 & disown

            sleep 1
        fi

        echo "========================================================"
        echo "Starting api agent..."
        echo "========================================================"

        python3 api_agent.py > /dev/null 2>&1 & disown

        sleep 3

        echo "========================================================"
        echo "Starting telegram bot..."
        echo "========================================================"

        python3 telegram_bot.py > /dev/null 2>&1 & disown

        sleep 2

        if [[ $OBJECT_DETECTOR_INSTALLED ==  "true" ]]; then

            echo "========================================================"
            echo "Starting object detector agent..."
            echo "========================================================"

            python3 object_detector_agent.py > /dev/null 2>&1 & disown
        fi
        ;;

    "stop")

        echo "========================================================"
        echo "Stopping app process..."
        echo "========================================================"

        kill_process api_agent.celery
        kill_process api_agent.py
        kill_process telegram_bot.py

        if [[ $OBJECT_DETECTOR_INSTALLED ==  "true" ]]; then

            kill_process motion_agent.celery
            kill_process object_detector_agent.py
        fi
        ;;

    "status")

        check_process api_agent.celery

        if [[ $OBJECT_DETECTOR_INSTALLED ==  "true" ]]; then

            check_process motion_agent.celery
            check_process object_detector_agent.py
        fi

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