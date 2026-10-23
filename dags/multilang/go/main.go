package main

import (
	"fmt"
	"log"

	"github.com/apache/airflow/go-sdk/airflow"
)

type order struct {
	ID     int `json:"id"`
	Amount int `json:"amount"`
}

type orders struct {
	Orders []order `json:"orders"`
}

func main() {
	bundle := airflow.Bundle()
	bundle.Register(
		newEtlDag(),
		airflow.TaskHandler("go_stub_etl", "transform", transform),
		airflow.TaskHandler("polyglot_etl", "extract", extract),
	)

	if err := bundle.Serve(); err != nil {
		log.Fatal(err)
	}
}

func newEtlDag() *airflow.DagRef {
	dag := airflow.Dag("go_etl", airflow.DagSpec{
		Queue: "golang",
		Tags:  []string{"multilang"},
	})

	extracted := dag.Task(extract)
	transformed := dag.Task(transform, airflow.Inputs(extracted))
	dag.Task(load, airflow.Inputs(transformed))

	return dag
}

func extract(airflow.Context) (orders, error) {
	return orders{Orders: []order{
		{ID: 1, Amount: 20},
		{ID: 2, Amount: 35},
		{ID: 3, Amount: 45},
	}}, nil
}

func transform(_ airflow.Context, data orders) (int, error) {
	total := 0
	for _, o := range data.Orders {
		total += o.Amount
	}
	return total, nil
}

func load(actx airflow.Context, total int) error {
	actx.Logger().InfoContext(actx, fmt.Sprintf("Total order amount: %d", total))
	return nil
}
