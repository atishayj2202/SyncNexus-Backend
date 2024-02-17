set -e
usage="Usage: sh deploy/staging.sh [migrate|build_push]"

export PROJECT_NAME=winged-octagon-413211

# docker details
export IMAGE_NAME=google-solution-challenge-backend
export IMAGE_VERSION=0.2.0-dev12
export SERVICE_NAME=google-solution-challenge-server
export REPOSITORY_NAME=google-solution-challenge-backend
export FULL_IMAGE_NAME=asia-south2-docker.pkg.dev/${PROJECT_NAME}/${REPOSITORY_NAME}/${IMAGE_NAME}:${IMAGE_VERSION}
export FLYWAY_CONTAINER_NAME=flyway/flyway:latest
export FLYWAY_CONFIG_PATH="$PWD"/keys/conf
export FLYWAY_MIGRATION_PATH="$PWD"/deploy/flyway/migrations


function build() {
  echo "building image ${FULL_IMAGE_NAME}"
  docker build -t "${FULL_IMAGE_NAME}" -f deploy/Dockerfile --platform linux/amd64 .
}

function check_version() {
  temp=$(gcloud artifacts docker tags list us-east4-docker.pkg.dev/${PROJECT_NAME}/${REPOSITORY_NAME}/${IMAGE_NAME} --filter="Tag:${IMAGE_VERSION}" --format=json)
  echo
  if [[ "$temp" == "[]" ]]; then
    echo "Tag doesn't exist in Artifact Registry. Proceeding ...."
  else
    echo "Tag already exists in Artifact Registry. Failing build."
    exit 1
  fi
}

if [[ $1 = "migrate" ]]
then
  docker run --rm \
  --network host \
  --mount type=bind,source="$FLYWAY_CONFIG_PATH",target=/flyway/conf \
  --mount type=bind,source="$FLYWAY_MIGRATION_PATH",target=/flyway/sql \
  $FLYWAY_CONTAINER_NAME -configFiles=/flyway/conf/flyway.conf migrate
elif [[ $1 = "build_push" ]]
then
  build
  docker push "${FULL_IMAGE_NAME}"
elif [[ $1 = "build" ]]
then
  build
elif [[ $1 = "push" ]]
then
  docker push "${FULL_IMAGE_NAME}"
elif [[ $1 = "check-version" ]]
then
  check_version
elif [[ $1 = "make-secret" ]]
then
  mkdir -p "keys/conf"
  echo "$(gcloud secrets versions access latest --secret="Service-Account-Credentials")" > keys/credentials.json
  echo "flyway.url=$(gcloud secrets versions access latest --secret="DB_URL")$(gcloud secrets versions access latest --secret="DB_NAME")" >> keys/conf/flyway.conf
  echo "flyway.user=$(gcloud secrets versions access latest --secret="DB_USER")" >> keys/conf/flyway.conf
  echo "flyway.password=$(gcloud secrets versions access latest --secret="DB_PASS")" >> keys/conf/flyway.conf
else
  echo "${usage}"
  exit 1
fi