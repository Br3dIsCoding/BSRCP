# BSRCP
BreadsStreamRedeemControlPanel - A control panel for 6 channel point redeems, with the option to enable / disable + change duration time

# ============== IMPORTANT STREAMER.BOT INSTRUCTIONS ============== #

1. Create a new Action (the name doesnt matter)

2. In the Triggers enter the normal twitch redeem (Right click + Add + Twitch + Channel Reward + Reward Redemption and then enter your redeem name)

3. In Sub-Action: Right click + Add + Core + System + Run a program

4. In the Target you enter the full path to the BSRCP.exe
   Example:  D:\TwitchRedeems\bsrcp_FOLDER\BSRCP.exe

5.In the Working Directory you enter the full path of the EXACT SAME FOLDER of where the .exe is
  Example:  D:\TwitchRedeems\bsrcp_FOLDER\   <----- Exactly the same as the Target BUT without the BSRCP.exe

6. In the Arguments enter BSRCP.exe --<and your redeem argument>
  These are the arguments for every redeem:
  --shuffle - Shuffle WASD
  --no_turn - No Turning
  --invert - Invert mouse
  --flip - Flip screen
  --noswear - No Swear
  --chaos - CHAOS

  Example: BSRCP.exe --flip    <------ for the flip screen redeem


How its supposed to look like:
![Example in Streamer.bot](https://github.com/Br3dIsCoding/BSRCP/blob/main/Example.png)



# ============== REDEEMS ============== #
1. Shuffle WASD - it shuffles randomly the WASD keys with one another (TO BE KNOWN THERE IS A 4.17% (1 out of 24) CHANCE OF THEM NOT CHANGING)
2. No Turning - Disables (as much as possible) the mouse movement, keeps the mouse centered on screen.
3. Invert mouse - Presses F9 (Yeah thats it) when playing games, make sure that there is a settings key for invert mouse, if there is change it to F9
4. Flip screen - Flips the screen verticly + IF USING VTUBE STUDIO flips your Vtube verticly
5. No Swear - uses mic detection + Whisper (OpenAI) to detect your mic and if you say one of the following words it will count it as a swear and it will vine boom you.
   The following swear words are: fuck,fucking,fucked,shit,shitty,bitch,bastard,ass,
    asshole,damn,goddamn,hell,crap,piss,pissed,dick,
    douche,slut,whore,bullshit,wtf,motherfucker,
    son of a bitch,cunt,jesus,christ,god and jesus christ almighty
6. CHAOS - Enables Flip screen + Shuffle WASD + No Turning | just CHAOS




# ============== GUI ============== #
In the GUI you will find these in order:

Changing the Chaos time + Enabling it
Changing the Shuffle WASD time + Enabling it
Changing the No Turning time + Enabling it
Changing the Invert Mouse time + Enabling it
Changing the Flip screen time + Enabling it

//No swearing is 120 seconds (2 minutes)

A button to start Chaos

A button to start Shuffle WASD

A button to start No turning

A button to start Invert Mouse

A button to start Flip Screen

drop down menu with all your mics, Please choose THE CORRECT MIC, if you won't there might be bugs with the swearing detection

A button to start No Swear

A live transcript Panel - when starting No Swear it will print out what you said, good for testing for the correct mic, try to say stuff like: "Hello whats up?", "Shit, Fuck, Bitch", "Yooo whats good man, Im good, fuck man this is hard", "the quick brown fox jumps over the lazy dog" (These are what I said while testing)

ANNNND thats all!
Enjoy letting your chat ruin your gaming expierence!🍞
