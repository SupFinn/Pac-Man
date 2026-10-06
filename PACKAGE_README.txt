==============================================================================
                              P A C - M A N
                      Ghosts! More ghosts! Waka waka!
==============================================================================


 QUICK START
 ------------------------------------------------------------------------------
  1. Extract the whole zip file (do not run the game from inside the zip).
  2. Run the program called "PacMan".
       Windows : double-click PacMan.exe
       Linux   : open a terminal in this folder and run ./PacMan
                 (if it says "permission denied", run: chmod +x PacMan)
  3. No installation and no Python are needed. Have fun!


 CONTROLS
 ------------------------------------------------------------------------------
    Move (1 player) ........ Arrow keys or W A S D
    Move (2 players) ....... Player 1: W A S D     Player 2: Arrow keys
    Select in menus ........ ENTER or SPACE
    Pause / resume ......... ESC  (or click the pause button)
    Back ................... ESC


 HOW TO PLAY
 ------------------------------------------------------------------------------
  * Eat every gum in the maze before the timer reaches zero to win the level.
  * Super gums (in the 4 corners) turn the ghosts blue: eat them while they
    run away to earn bonus points. Eaten ghosts come back after a moment.
  * Grab the KEY to open the side tunnel, a great escape route.
  * Touching a normal ghost costs one life. You start with 3 lives.
  * Levels 1-10 are the main game. Levels 11-20 are optional bonus levels.
  * At the end of a game, enter your name (3 to 10 letters, digits or spaces)
    to save your score in the top 10.


 CHEAT KEYS  (for testing, press the same key again to turn it off)
 ------------------------------------------------------------------------------
    F1 ..... Invisibility   Ghosts cannot see you
    F2 ..... Ghost freeze   All ghosts stop moving
    F3 ..... God mode       You cannot lose a life
    F4 ..... Skip level     Win the current level instantly


 CONFIGURATION
 ------------------------------------------------------------------------------
  The settings are in the file "config.json", inside the "_internal" folder.
  Open it with any text editor. Lines starting with # or // are comments.

    highscore_filename ........ name of the highscore file (must end in .json)
    lives ..................... number of lives
    points_per_pacgum ......... points for a gum
    points_per_super_pacgum ... points for a super gum
    points_per_ghost .......... points for an eaten ghost
    seed ...................... seed used to generate the mazes
    levels .................... list of levels, each with:
                                  width, height  (between 10 and 40)
                                  max_time       (time limit in seconds)

  Tip: make a copy of config.json before editing it. If the game shows an
  error message after your change, restore the copy.


 HIGHSCORES
 ------------------------------------------------------------------------------
  Scores are saved in a folder called ".pacman" in your home folder:
    Windows : C:\Users\<your name>\.pacman\
    Linux   : /home/<your name>/.pacman/
  Delete the file in that folder to reset the scoreboard.


 TROUBLESHOOTING
 ------------------------------------------------------------------------------
  * Windows says "Windows protected your PC":
      Click "More info", then "Run anyway". It appears because the game is
      not digitally signed, it is safe.
  * The game does not start on Linux:
      Run "chmod +x PacMan" in this folder, then "./PacMan".
  * No sound or no video background:
      Make sure you extracted the whole zip and did not move or delete the
      "_internal" folder. It must stay next to the PacMan program.


 ------------------------------------------------------------------------------
                       Made with love by EYOMI & FINN
==============================================================================