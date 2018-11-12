# Genrenome
An attempt to see how people's personality affects their taste in music and vice-versa.
This application is a toll used to assist in the data collection for the task defined below.

---------------
### A Correlation between Music and Personality

- We ask volunteers to provide us with 5 of their favourite songs.
- We characterise these songs by Genre and then create a music profile for each individual.
- We also use tests to determine the personality type of the individual using the OCEAN model of personality.
- We then try and find a correlation between the taste in music and the personality type of the individual.

There have been studies done that show a relation between your personality and the type of music you like to listen to. We would like to find an underlying relationship between the type of music a person listens to, i.e. his music profile and use that to accurately predict their personality.

There are literally thousands of genres of music and we would like to find out if there is a relation between genre and personality. We select a set of broad genres and ask volunteers to do tasks similar to the ones they did before while listening to music from these genres.

--------------------

### Installation instructions
```
./configure

```
### Setup
Please go through the setup tutorial present [here](#).

### Running the application
```
source venv/bin/activate
python app.py [host address] [port]
```
Example: `python app.py 0.0.0.0 8081`


### Theory
Scoring of Big Five model personality done on the basis of the following quiz:
https://openpsychometrics.org/printable/big-five-personality-test.pdf
