# A telegram bot made with Flask and Aiogram

## Run with docker
1. Change `<YOUR TOKEN>` in **bot/Dockerfile** to your telegram token
2. Run `docker compose build`
3. Run `docker compose up` (`docker compose up -d` to run in background)

## Run without docker
1. Create `.env` file in `bot/` directory and write the following lines:<br/>
`TOKEN=<YOUR TOKEN>`<br/>
`IP=http://localhost:5000/`
2. Create virtual environment (optionally)<br/>
`python -m venv venv` or `python3 -m venv venv`<br/>and activate<br/>
for Linux: `source ./venv/bin/activate`<br/>
for Windows: `./venv/Scripts/activate`
3. Install requirements.txt<br/>
`pip install -r requirements.txt`
4. Make database migrations<br/>
`flask --app="API/run.py" db init`<br/>
`flask --app="API/run.py" db migrate`<br/>
`flask --app="API/run.py" db upgrade`
5. Run `API/run.py` and `bot/run_bot.py` with `-m` flag<br/>
`python -m API.run`<br/>`python -m bot.run_bot`

