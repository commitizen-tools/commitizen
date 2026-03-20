Require cz

# Use bash for cross-platform compatibility (macOS, Linux, Windows)
Set Shell bash

Set FontSize 16
Set Width 878
Set Height 568
Set Padding 20
Set TypingSpeed 50ms

Set Theme {
  "name": "Commitizen",
  "black": "#232628",
  "red": "#fc4384",
  "green": "#b3e33b",
  "yellow": "#ffa727",
  "blue": "#75dff2",
  "magenta": "#ae89fe",
  "cyan": "#708387",
  "white": "#d5d5d0",
  "brightBlack": "#626566",
  "brightRed": "#ff7fac",
  "brightGreen": "#c8ed71",
  "brightYellow": "#ebdf86",
  "brightBlue": "#75dff2",
  "brightMagenta": "#ae89fe",
  "brightCyan": "#b1c6ca",
  "brightWhite": "#f9f9f4",
  "background": "#1e1e2e",
  "foreground": "#afafaf",
  "cursor": "#c7c7c7"
}

Hide

Sleep 1s

Type "PS1='$ '"
Enter
Sleep 300ms

Type "rm -rf /tmp/commitizen-example && mkdir -p /tmp/commitizen-example && cd /tmp/commitizen-example"
Enter
Sleep 500ms
