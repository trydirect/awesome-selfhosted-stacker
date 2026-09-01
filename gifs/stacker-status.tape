Output gifs/stacker-status.gif

Set FontSize 16
Set Width 1200
Set Height 500
Set Padding 20
Set Theme "Dracula"
Set TypingSpeed 50ms

Type "$ stacker status"
Enter
Sleep 1s

Type "CONTAINER              IMAGE            STATUS                  PORTS"
Enter
Type "project-ghost-1        ghost:5-alpine   Up 2 minutes            0.0.0.0:2368->2368/tcp"
Enter
Type "project-mysql-1        mysql:8          Up 2 minutes (healthy)  0.0.0.0:3306->3306/tcp"
Sleep 500ms
Enter
Enter

Type "$ curl -sf http://94.130.99.220:2368/ | head -3"
Enter
Sleep 500ms

Type '<!DOCTYPE html>'
Enter
Type '<html lang="en">'
Enter
Type '<head>'
Enter
Sleep 2s
