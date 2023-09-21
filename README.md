# Project2_FoodRecommendationBot

## To crete virtual env
python -m venv venv

## Switch to virtual env
./venv/Scripts/activate

## To install rasa and discord.py
pip install -r requirements.txt

## To train model
rasa train

## To enable action server
rasa run actions

## To run rasa shell
rasa shell

## To run server
python DiscordBot.py
