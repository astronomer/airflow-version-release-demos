#!/usr/bin/env bash
set -euo pipefail

GRADLE_IMAGE="gradle:8.14.5-jdk11@sha256:d2e614a94917485def484cd411b7d940edfb5bdc7570ab7a66adf0c49e197570"
AIRFLOW_REPO="${AIRFLOW_REPO:-$HOME/code/apache/airflow}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DAG_DIR="$(cd "$PROJECT_DIR/../../dags/multilang/java" && pwd)"

docker run --rm --platform linux/arm64 \
  -v "$AIRFLOW_REPO":/airflow:ro \
  -v "$PROJECT_DIR":/project:ro \
  -v "$DAG_DIR":/dag \
  -v airflow_java_sdk34_gradle_cache:/home/gradle/.gradle \
  -v airflow_java_sdk34_m2:/root/.m2 \
  "$GRADLE_IMAGE" \
  bash -euo pipefail -c "
    mkdir -p /src/airflow-core/src/airflow/serialization /build/src/main/java/com/astronomer/demo
    cp -r /airflow/java-sdk /src/java-sdk
    rm -rf /src/java-sdk/build /src/java-sdk/*/build /src/java-sdk/.gradle
    cp /airflow/airflow-core/src/airflow/serialization/schema.json /src/airflow-core/src/airflow/serialization/
    cd /src/java-sdk
    gradle --no-daemon --console=plain publishToMavenLocal -PskipSigning=true
    cp /project/build.gradle /project/settings.gradle /project/gradle.properties /build/
    cp /dag/*.java /build/src/main/java/com/astronomer/demo/
    cd /build
    gradle --no-daemon --console=plain bundle
    cp build/bundle/java-etl-all.jar /dag/java_etl.jar
    chown $(id -u):$(id -g) /dag/java_etl.jar
  "
