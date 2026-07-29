// Go SDK bundle for the go_task_syntax_example DAG.
//
// The Dag itself is authored in Python (dags/go_sdk/go_task_syntax_example.py).
// Only the `transform` task runs in Go: the Python `extract` task pushes a
// value to XCom, this Go task reads it, sums the numbers in Go, and returns a
// result map (pushed as transform's return_value XCom), which the Python
// `load` task then reads and prints. This exercises XCom across the language
// boundary in both directions.
//
// Build (cross-compiled for the linux/arm64 Airflow container) with:
//
//	go mod tidy
//	go tool airflow-go-pack --goos linux --goarch arm64 \
//	    --output ./bin/go_task_syntax_example .
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"log/slog"
	"runtime"

	v1 "github.com/apache/airflow/go-sdk/bundle/bundlev1"
	"github.com/apache/airflow/go-sdk/bundle/bundlev1/bundlev1server"
	"github.com/apache/airflow/go-sdk/sdk"
)

// Overridable at build time via -ldflags; the packer also stamps these.
var (
	bundleName    = "go_task_syntax_example"
	bundleVersion = "1.0.0"
)

type bundle struct{}

var _ v1.BundleProvider = (*bundle)(nil)

func (b *bundle) GetBundleVersion() v1.BundleInfo {
	return v1.BundleInfo{Name: bundleName, Version: &bundleVersion}
}

// RegisterDags maps Go task functions to the Python stub DAG. The dag_id must
// match the Python @dag dag_id, and each AddTask function name must match a
// @task.stub function name.
func (b *bundle) RegisterDags(dagbag v1.Registry) error {
	d := dagbag.AddDag("go_task_syntax_example")
	d.AddTask(transform)
	return nil
}

func main() {
	if err := bundlev1server.Serve(&bundle{}); err != nil {
		log.Fatal(err)
	}
}

func transform(ctx sdk.TIRunContext, client sdk.Client, logger *slog.Logger) (any, error) {
	ti := ctx.TaskInstance()

	raw, err := client.GetXCom(ctx, ti.DagID, ti.RunID, "extract", nil, "return_value", nil)
	if err != nil {
		return nil, fmt.Errorf("reading extract XCom: %w", err)
	}
	logger.Info("read upstream Python XCom", "from_task", "extract", "value", raw)

	// raw is a decoded msgpack value: a map whose integers arrive as the
	// smallest fitting Go type (3 -> int8), not float64. Round-trip through JSON
	// to land it in a typed struct instead of hand-handling each numeric type.
	var payload struct {
		Numbers []float64 `json:"numbers"`
	}
	encoded, err := json.Marshal(raw)
	if err != nil {
		return nil, fmt.Errorf("re-encoding extract payload: %w", err)
	}
	if err := json.Unmarshal(encoded, &payload); err != nil {
		return nil, fmt.Errorf("decoding extract payload: %w", err)
	}

	var sum float64
	for _, n := range payload.Numbers {
		sum += n
	}

	result := map[string]any{
		"sum":         sum,
		"count":       len(payload.Numbers),
		"computed_by": "Go " + runtime.Version(),
	}
	logger.Info("computed result in Go", "result", result)
	return result, nil
}
