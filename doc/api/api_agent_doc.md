# API agent documentation

Receives requests and interacts with the rest of system elements .

Below are the set of requests that can be made to this API and the values it returns.

## Make a photo

Send a request to take a photo. The photo format is jpg.

- API-URL: `/api/take_photo`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message and task id.

**Example:**

\> Request:

```
POST --> /api/take_photo -- data = {'user': 'username', 'password': 'password'}
```
\> Response:

```
200 --> {
            "status": "Photo request has been sent",
            "task_id": "63ed3b99-be6f-424b-a27f-4c57c9662439"
        }
```


## Record a video

Send a request to record a video. The video format is mp4.

- API-URL: `/api/record_video`
- Method: *POST*
- Data: 
    + Authentication info.
     + (optional) record_time (record time in seconds)
- Returns: Status message and task id.

**Example:**

\> Request:

```
POST --> /api/record_video -- data = {'user': 'username', 'password': 'password', 'record_time': 15}
```
\> Response:

```
200 --> {
            "status": "A 10 seconds video request has been sent",
            "task_id": "204213ad-3bd2-4036-8441-2cbd86f463ff"
        }
```


## Check task status

Send a request to check a task status. For example, you can check a recording video task status.


- API-URL: `/api/check/<task_id>`
- Method: *GET*
- Data: 
    + Authentication info.
- Returns: Task status. ['PENDING','STARTED','FAILURE',RETRY,'REVOKED','SUCCESS']

**Example:**

\> Request

```
GET --> /api/check/204213ad-3bd2-4036-8441-2cbd86f463ff -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "SUCCESS"
        }
```

## Get task result

Send a request to get a task result

- API-URL: `/api/result/<task_id>`
- Method: *GET*
- Data: 
    + Authentication info.
- Returns: . If task has finished, then returns status and result, 
otherwise only will return the task status.

**Example:**

\> Request

```
GET  --> /api/result/204213ad-3bd2-4036-8441-2cbd86f463ff -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "ready": true,
            "result": "/home/jmv74211/Escritorio/security_files/videos/VID_20190727_184309.mp4",
            "status": "SUCCESS"
        }
```

## Stop task

You can send a request to stop a task that is in progress. For instance, this is useful when you have sent
a request to record a long video, and you want to stop it to make another thing.

- API-URL: `/api/stop/<task_id>`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/stop/204213ad-3bd2-4036-8441-2cbd86f463ff -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "Task 204213ad-3bd2-4036-8441-2cbd86f463ff has been stopped successfully"
        }
```

## Activate motion agent

It starts motion agent process to activate automatic mode, in which motion sensor will detect
motion and it will take a photo or record video, and finally, it will sent an alert to main api agent.

- API-URL: `/api/motion_agent/activate`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/motion_agent/activate -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "The motion agent in photo mode has been activated sucessfully"
        }
``` 

## Deactivate motion agent

It stops motion agent process to change mode.

- API-URL: `/api/motion_agent/deactivate`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/motion_agent/deactivate -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "The motion agent has been deactivated sucessfully"
        }
``` 

## Check motion agent status

Request to check the motion agent status.

- API-URL: `/api/motion_agent/check_status`
- Method: *GET*
- Data: 
    + Authentication info.
- Returns: Motion agent status.

**Example:**

\> Request

```
GET --> /api/motion_agent/check_status -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "OFF"
        }
``` 

## Generate an alert

Request to generate an alert. This request usually comes from the motion agent when a motion alert has been detected.

- API-URL: `/api/motion_agent/generate_alert`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/motion_agent/generate_alert -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "status": "The alert has been received"
        }
```

## Check alert

Request to check if exist an alert in main api agent. This alert is consumed by the request sender.

- API-URL: `/api/motion_agent/check_alert`
- Method: *GET*
- Data: 
    + Authentication info.
- Returns: True and file_path if there is an alert, False otherwise.

**Example:**

\> Request

```
GET --> /api/motion_agent/check_alert -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {
            "alert": True,
            "file_path": /home/jmv74211/Escritorio/security_files/videos/VID_20190727_184309.mp4
        }
```

## Activate streaming

Request to activate the streaming server.

- API-URL: `/api/streaming/activate`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/streaming/activate -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {   
            "status": "The streaming mode has been activated sucessfully"
        }
```

## Deactivate streaming

Request to deactivate the streaming server.

- API-URL: `/api/streaming/deactivate`
- Method: *POST*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
POST --> /api/streaming/deactivate -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {   
            "status": "The streaming server has been stopped sucessfully"
        }
```

## Check streaming status

Request to check the streaming server status.

- API-URL: `/api/streaming/check_status`
- Method: *GET*
- Data: 
    + Authentication info.
- Returns: Status message.

**Example:**

\> Request

```
GET --> /api/streaming/check_status -- data = {'user': 'username', 'password': 'password'}
```

\> Response:

```
200 --> 
        {   
            "status": "ON"
        }
```