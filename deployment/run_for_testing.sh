export db_type=sqlite
export meal_db_path=./deployment/meals.db
export port_run=15001

# If the service is already running, stop it first
docker-compose -f deployment/docker-compose.yml down

docker-compose -f deployment/docker-compose.yml up -d

# Run the backend with the project environment (identical to the Docker image)
if [ ! -x .venv/bin/python ]; then
  echo "Project environment not found. Create it with:"
  echo "  python -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

.venv/bin/python src/main.py
