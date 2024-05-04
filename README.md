# Getting started
## First steps
```
git clone https://github.com/lildimasta/todolist_tg_bot
pip install -r requirements.txt
```
## Configure environment variables
### Create .env file
```
vim .env
#or
nano .env
```
## In .env file
### Bot settings
```
#example
BOT_TOKEN='123232321'
```
### Database
```
#example
DATABASE_NAME='postgres'
DATABASE_USER='postgres'
DATABASE_PASSWORD='qwerty'
DATABASE_HOST='localhost'
DATABASE_PORT='5432'
```
# Run project
```
python3 -m bot
```
