# blackboard-export

Dump all listed 'x-bb-file' and 'x-bb-document' attachments from a list of
user-specified courses using Blackboard Learn APIs. Works for CUHK(SZ).

## Dependencies

- requests
- BeautifulSoup

## Usage

Specify EXPORT_PATH. By default, all files will be dumped to 'new_courses'

Specify COURSES. It should be a list of course_id, which can be found in course URL. If you don't specify this the script will do nothing.

```python
COURSES = ['_110_1', '_115_1', '_237_1', '_245_1', '_113_1']
```

TODO: Automate this process.

## Disclaimer

This script should be regarded as an alpha version whose only purpose is to demonstrate the usage of Blackboard Learn REST APIs. The author is not trained in a CS program and the only reason he wrote this script is that, like everybody else in this University, he founds Blackboard sucks and wants Moodle back. Thus, this script is by no means complete or stable. For example, it will NOT fetch announcements, calendars, or implicitly listed attachments for you. You may run the script only if you understand how it works and do so entirely AT YOUR OWN RISK. I will laugh at you if you missed a deadline or attracted a warning letter from ITSO because of a hidden failure of the script.
