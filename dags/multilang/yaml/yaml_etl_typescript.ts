import { Bundle, TaskHandler } from "apache-airflow-ts-sdk";

interface Order {
  id: number;
  amount: number;
}

interface OrderData {
  orders: Order[];
}

function extract(): OrderData {
  return {
    orders: [
      { id: 1, amount: 20 },
      { id: 2, amount: 35 },
      { id: 3, amount: 45 },
    ],
  };
}

function transform({ data }: { data: OrderData }): number {
  return data.orders.reduce((sum, order) => sum + order.amount, 0);
}

function load({ total }: { total: number }): void {
  console.log(`Total order amount: ${total}`);
}

await new Bundle(
  new TaskHandler("yaml_etl_typescript", "extract", extract),
  new TaskHandler("yaml_etl_typescript", "transform", transform),
  new TaskHandler("yaml_etl_typescript", "load", load),
).serve();
