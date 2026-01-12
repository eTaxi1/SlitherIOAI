Implementing AI into game
- Reward
- observables
- Reset
- 


player spawns -> 0,0, 10, 10, 
player dies on snake drops food -> 0,0, 10,10

10 segments are worth 10 score 1 segment is worth 1 score 

- - - --  -- -- - - - - 
score = radius of food/10. radius of 10 gives 1 score
player starts on score of 10 with 10 segments with       
1 of those segments is worth 1 score
gains 3 score to get 1 segment








[10][12][12]
[1][11][12]
[3][4][5]


[1][1][1]
[1][][1]
[1][1][1]



00             04
[]   []   []   []                             
[]   []   []   []
[]   []   []   []
[]   []   []   []
40             44



TODO 
- Write helper functions in MainGame for CustomEnv
- Improve Oberservables 
- Update Snake positions in the step function 


WARNING: SEGMENTS ARENT ADDED TO CELL IN UPDATE CORRECTLY



-  Balance size/score in game. 



Long term:
Add AI that make random moves to learning. Plot random AI vs Trained AI performance
Add Ability to play vs AI




