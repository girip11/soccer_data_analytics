# Data exploration

## Events

Fields are

- event_id - Id of the event
- half_time - possibly indicating if the events happened in the first or second half. Dataset contains events within one half.
- time - time of the event in seconds
- player_id - player identifier (22 players)
- team_id - team identifier(2 teams)
- event - Event that happened

Type of events are

- 'Kick Off'
- 'Pass'
- 'Cross' - a medium-to-long-range pass from a wide area of the field towards the centre of the field near the opponent's goal.
- 'Reception'
- 'Interception'
- 'Clearance' - when a player kicks the ball away from the goal they are defending.
- 'Ball Out of Play' - No player and team specified
- 'Throw in'
- 'Freekick'
- 'Defensive Event' - defender tried defending?
- 'Ball Progression' - Possible the player progresses in the field with the ball
- 'Goalkick'
- 'Attempt at Goal'
- 'Corner'

Events are captured in the chronological order in the provided dataset. Time period seems to be about approximately between 10.5 to 20.5 minutes

## Tracking

Seems like we have tracking data for 600 seconds which is 10 minutes. Tracking events are captured every 40ms. As per this dataset, every 40ms we receive exactly 23 data points. Out of those 23 data points, the first one always contains -1 for id_actor and id_team(delimiting purpose). So we do have 22 useful data points capturing the position of 22 players (11 per team) on the field.

Fields are

- id_half - indicates which half of the play we are tracking
- t - time in milliseconds because with seconds it can't get to `60000`
- id_actor - Player id
- id_team - team id
- x - position of player
- y - position of player

We might have to offset the time in the tracking dataset to use with the events dataset.

There are some data points with actor and team but either x or y or both seems to be negative(excluding those -1 datapoints). There are 2480 such data points. May be they were slightly outside the boundaries. Sometimes due to corner kick, throw in, fetching out of play ball etc.
