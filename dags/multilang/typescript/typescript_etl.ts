import { Bundle, Dag, TaskHandler } from "apache-airflow-ts-sdk";

interface Order {
  id: number;
  amount: number;
}

interface OrderData {
  orders: Order[];
}

const dag = new Dag("typescript_etl", { tags: ["multilang"], queue: "typescript" });

const extract = dag.task(function extract(): OrderData {
  return {
    orders: [
      { id: 1, amount: 20 },
      { id: 2, amount: 35 },
      { id: 3, amount: 45 },
    ],
  };
});

const transform = dag.task(function transform({ data }: { data: OrderData }): number {
  return data.orders.reduce((sum, order) => sum + order.amount, 0);
});

const load = dag.task(function load({ total }: { total: number }): void {
  console.log(`Total order amount: ${total}`);
});

load({ total: transform({ data: extract() }) });

function sumOrders({ data }: { data: OrderData }): number {
  return data.orders.reduce((sum, order) => sum + order.amount, 0);
}

function printTotal({ total }: { total: number }): void {
  console.log(`Total order amount: ${total}`);
}

await new Bundle(
  dag,
  new TaskHandler("typescript_stub_etl", "transform", sumOrders),
  new TaskHandler("polyglot_etl", "load", printTotal),
).serve();
 