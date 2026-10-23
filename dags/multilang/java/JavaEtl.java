package com.astronomer.demo;

import java.util.List;
import java.util.Map;
import org.apache.airflow.sdk.Airflow;
import org.apache.airflow.sdk.Bundle;
import org.apache.airflow.sdk.Server;

@Airflow.Dag(id = "java_etl", tags = {"multilang"})
public class JavaEtl {

  @Airflow.Task(id = "extract", queue = "java")
  public Map<String, List<Map<String, Long>>> extract() {
    return Map.of(
        "orders",
        List.of(
            Map.of("id", 1L, "amount", 20L),
            Map.of("id", 2L, "amount", 35L),
            Map.of("id", 3L, "amount", 45L)));
  }

  @Airflow.Task(id = "transform", queue = "java")
  public long transform(Map<String, List<Map<String, Long>>> data) {
    return data.get("orders").stream().mapToLong(order -> order.get("amount")).sum();
  }

  @Airflow.Task(id = "load", queue = "java")
  public void load(long total) {
    System.out.println("Total order amount: " + total);
  }

  @Airflow.Deps
  static class Wiring implements JavaEtlDeps {
    void depends() {
      load(transform(extract()));
    }
  }

  public static void main(String[] args) {
    Server.create(args).serve(new Bundle().register(JavaEtl.class).register(StubHandlers.class));
  }
}
