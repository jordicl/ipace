
# btt.py
The `btt.py` script is an example script that uses the [jlrpy](https://github.com/ardevd/jlrpy) module to print some useful information about your Jaguar iPace to standard out. It's main use is to display that information on the touchbar of recent Macbook Pro's, but it can be executed fromt the command line as well. To display information on the touchbar, an additional tool is needed: [BetterTouchTool](https://folivora.ai). Quick setup:

1. Download the project.
2. Add a file `.ipace.conf` to your home directory. It should contain:
```
[credentials]
email=<Email address>
password=<Password>
```
3. Add a custom widget of type "Run Shell Script and Show Return Value".
4. Put in the correct path to the `btt.py` script.  

NOTE: The script provides a few command line options. Use `btt.py -h` to display.


NOTE: this script is very much WIP and still contains a bunch of spaghetti code :-)