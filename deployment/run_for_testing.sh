export db_type=sqlite
export meal_db_path=./deployment/meals.db
export port_run=15001

docker-compose -f deployment/docker-compose.yml up -d

python3 src/main.py