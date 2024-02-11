set -e
usage="Usage: sh deploy/local_test.sh [build|push]"

export COCKROACH_CONTAINER_NAME=cockroachdb/cockroach:v21.2.7
export COCKROACH_DB_LOCAL_URL="cockroachdb://root@localhost:26257/defaultdb?sslmode=disable"
export COCKROACH_DATA_PATH="$PWD"/cockroach-data/
export GOOGLE_CLOUD_SQL_CONNECTION="winged-octagon-413211:asia-south2:google-solution-challenge"
export GOOGLE_CLOUD_SQL_CREDENTIALS_FILE="$PWD"/keys/winged-octagon-413211-ce95d7afb9ff.json


function get_container() {
    docker ps --filter "ancestor=${1}" --format '{{.ID}}' | sed -n 1p
}

function add_sql() {
  container=$(get_container $COCKROACH_CONTAINER_NAME)
  folder="$PWD"/deploy/flyway/migrations/*
  for file in $folder; do
    if [ -f "$file" ]; then
        file_name=$(basename "$file")
        echo "Running file: $file_name"
        docker exec "$container" bash -c "cat /migrations/$file_name | cockroach sql --insecure"
    fi
done
}

if [[ $1 = "pull" ]]
then
  docker pull "${COCKROACH_CONTAINER_NAME}"
elif [[ $1 = "local-start" ]]
then
  port=26257
  out_port=26258
  echo "creating directory ${COCKROACH_DATA_PATH}"
  # rm data directory
  rm -rf "$COCKROACH_DATA_PATH"
  mkdir "$COCKROACH_DATA_PATH"
  docker run -i \
      --mount type=bind,source="$PWD"/deploy/flyway/migrations,target=/migrations \
      --mount type=bind,source="$COCKROACH_DATA_PATH",target=/cockroach/cockroach-data \
      -d -p "$out_port":"$port" -p 8081:8080 $COCKROACH_CONTAINER_NAME start-single-node --insecure
  sleep 1
  container=$(get_container $COCKROACH_CONTAINER_NAME)
  add_sql
elif [[ $1 = "local-run" ]]
then
  container=$(get_container $COCKROACH_CONTAINER_NAME)
  docker exec "$container" bash -c "echo '${2}' | cockroach sql --insecure"
elif [[ $1 = "stop" ]]
then
  docker container stop "$(get_container $COCKROACH_CONTAINER_NAME)"
  rm -rf "$COCKROACH_DATA_PATH"
elif [[ $1 = "test" ]]
then
  echo "Running tests"
  source .env
  doppler run poetry run pytest
elif [[ $1 = "check-format" ]]
then
  isort src tests  -c --diff && black src tests  --diff --check
elif [[ $1 = "format" ]]
then
  isort src tests  && black src tests
elif [[ $1 = "build-local-env" ]]
then
  poetry env use ~/.pyenv/versions/3.10.12/bin/python
  poetry install
  sh deploy/local_test.sh pull
elif [[ $1 = "pull-auth-proxy" ]]
then
  curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.2/cloud-sql-proxy.darwin.arm64
  chmod +x cloud-sql-proxy
elif [[ $1 = "remote-start-test" ]]
then
  ./cloud-sql-proxy $GOOGLE_CLOUD_SQL_CONNECTION --credentials-file=$GOOGLE_CLOUD_SQL_CREDENTIALS_FILE --unix-socket="./keys/"
elif [[ $1 = "remote-start-data" ]]
then
  ./cloud-sql-proxy $GOOGLE_CLOUD_SQL_CONNECTION --credentials-file=$GOOGLE_CLOUD_SQL_CREDENTIALS_FILE --port=3308
else
  echo "${usage}"
  exit 1
fi