## Testing

Once everything has been installed and configured, you can check if it has really been done correctly by running the 
tests located in the `test` directory. Inside there will be two directories, `unit` for the unit tests and `integration` for 
the integration tests. You can run all the tests using the following commands:

**Unit test**

```Bash
python3 -m unittest discover -s [unit test path] -t [unit test path]
```

*example:*

```Bash
python -m unittest discover -s /home/jmv74211/git/TFM_security_system_PI/test/unit -t /home/jmv74211/git/TFM_security_system_PI/test/unit
```

**Integration test**

```Bash
python3 -m unittest discover -s [integration test path] -t [unit test path]
```

*example:*

```Bash
python -m unittest discover -s /home/jmv74211/git/TFM_security_system_PI/test/integration -t /home/jmv74211/git/TFM_security_system_PI/test/integration
```