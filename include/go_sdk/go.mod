module github.com/astronomer/airflow-version-release-demos/include/go_sdk

go 1.25.0

tool github.com/apache/airflow/go-sdk/cmd/airflow-go-pack

require github.com/apache/airflow/go-sdk v0.0.0-00010101000000-000000000000

require (
	github.com/inconshreveable/mousetrap v1.1.0 // indirect
	github.com/spf13/cobra v1.10.1 // indirect
	github.com/spf13/pflag v1.0.10 // indirect
	github.com/vmihailenco/msgpack/v5 v5.4.1 // indirect
	github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
)

replace github.com/apache/airflow/go-sdk => /go-sdk
