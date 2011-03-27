Log2Text.exe
  -  is a windows executible that parses a .dat file from the broadwin archive and generates a fixed format text file.
  - it should be run in a directory containing a subdirectory for each <tag>
  - it is run as Log2Text <tag> <option> <year> <month>
  - it reads ./<tag>/<tag>$<year>[<month>]<option>.DAT
  - it produces ./<tag>$<year>[<month>]<option>.TXT

This text file contains csv  lines in the format

YYYY-MM-DD, HH:MM:SS, XXXX,  D.DD, D.DD, D.DD, D.DD

Generally only the first of these is of much use.

Like so much in buildings, the metadata is embeddedin the filename.  

To understand the points you can use the broadwin scada tool.  You will have to
download the plugin.  It only runs in explorer.  Login with ucb and same as passwd.

http://saturn.dofm.berkeley.edu/broadWeb/system/bwviewpg.asp?proj=UCProject&node=UCB_SODAHALL&goto=graph=ZONEMAP.bgr&tool=1&capt=1&stat=1
