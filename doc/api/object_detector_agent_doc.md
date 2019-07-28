# Object detector agent documentation

Receives requests, processes an image and returns the set of objects detected in that image.

Below are the set of requests that can be made to this API and the values it returns.

## Get objects from an image

Send a request to

- API-URL: `/api/detector`
- Method: *GET*
- Data: 
    + file_path: Image file path
- Returns: Objects detected list and its score(probability).

**Example:**

From this image, the following result has been obtained:

<p align="center">
  <img src="https://raw.githubusercontent.com/jmv74211/TFM_security_system_PI/master/backend_app/src/modules/object_detector/test_images/2.jpg">
</p>


\> Request:

```
GET --> /api/detector -- data = {'file_path': '/home/jmv74211/test_images/photo1.jpg'}
```

\> Response:

```
200 --> {
    "objects": [
        {
            "person": 0.9420067667961121
        },
        {
            "person": 0.9036192893981934
        },
        {
            "cup": 0.8740732669830322
        },
        {
            "person": 0.8543923497200012
        },
        {
            "person": 0.844074010848999
        },
        {
            "person": 0.5493395924568176
        },
        {
            "laptop": 0.5382046699523926
        }
    ]
}
```