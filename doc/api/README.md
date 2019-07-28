# API documentation

The backend application basically consists of 3 agents and a series of modules that they use to communicate with the
hardware resources.

Both the api agent and the object detector agent implement a restful API. Regarding the motion agent, it is initiated 
as a process whose function is to generate alerts in the api agent.

Next, it is shown the set of requests that can be made both to the API agent and to the object detector agent.

## API agent

This agent is the principal. Through it, we will be able to carry out all the activities of the application.

You can see the set of requests with some examples in [this documentation](https://github.com/jmv74211/TFM_security_system_PI/blob/master/doc/api/api_agent_doc.md).

## Object detector agent

This is an agent in charge of detecting objects in an image. It is also implemented as a restful API, 
since in the future it is intended to be able to add new related functionalities.

You can see the set of requests with some examples in 
[this documentation](https://github.com/jmv74211/TFM_security_system_PI/blob/master/doc/api/object_detector_agent_doc.md).



