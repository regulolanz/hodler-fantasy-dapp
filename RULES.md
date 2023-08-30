# Fantasy Rules for Hodler-Fantasy-Dapp

The following rules define how fantasy points are awarded to players based on their performance in matches.

## Scoring System

| PARAMETER                    | CONDITION                                | POINTS |
|------------------------------|------------------------------------------|--------|
| Minutes Played               | < 60min                                  | 1      |
| Minutes Played               | > 60min                                  | 2      |
| Goal                         | Position: GOA / DEF                      | 6      |
| Goal                         | Position: MID                            | 5      |
| Goal                         | Position: STR                            | 4      |
| Goal Assist                  | Last pass that causes a goal             | 3      |
| Clean Sheet (GOA)            | Having played > 60min                    | 4      |
| Clean Sheet (DEF)            | Having played > 60min                    | 3      |
| Clean Sheet (MID)            | Having played > 60min                    | 2      |
| Clean Sheet (STR)            | Having played > 60min                    | 1      |
| Missed penalty               | Regardless of the player's demarcation   | -2     |
| Saved penalty                | The goalkeeper intercedes in the arrest  | 5      |
| Provoked penalty             | Regardless of the player's demarcation   | 2      |
| Penalty committed            | Regardless of the player's demarcation   | -2     |
| Conceded Goals (GOA / DEF)   | EVERY 2                                  | -2     |
| Conceded Goals (MID / STR)   | EVERY 2                                  | -1     |
| Yellow Card                  | Regardless of the player's demarcation   | -1     |
| Second Yellow Card           | Regardless of the player's demarcation   | -1     |
| Red Card                     | Regardless of the player's demarcation   | -3     |

## Hodler Mark

The Hodler Mark is a unique score given by the coach after the game based on a player's performance in the match. The points awarded can range from 1 to 5.

---

### Acknowledgments

The fantasy points calculation in this project is inspired by [LaLiga Fantasy MARCA](https://fantasy.laliga.com/). LaLiga Fantasy MARCA is an online fantasy football platform where users pick players, prepare line-ups, and create a league. In the future, we may revise how fantasy points are calculated, but for the current version of this project, we've used the LaLiga Fantasy MARCA's system as a reference.