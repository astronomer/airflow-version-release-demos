package com.astronomer.demo;

import java.util.List;
import java.util.Map;
import org.apache.airflow.sdk.Airflow;

public class StubHandlers {

  @Airflow.TaskHandler(dag = "java_stub_etl", task = "transform")
  public long transform(Map<String, List<Map<String, Object>>> data) {
    return sumAmounts(data);
  }

  @Airflow.TaskHandler(dag = "polyglot_etl", task = "transform")
  public long polyglotTransform(Map<String, List<Map<String, Object>>> data) {
    return sumAmounts(data);
  }

  private static long sumAmounts(Map<String, List<Map<String, Object>>> data) {
    return data.get("orders").stream()
        .mapToLong(order -> ((Number) order.get("amount")).longValue())
        .sum();
  }
}
