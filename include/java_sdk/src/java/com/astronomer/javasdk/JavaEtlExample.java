package com.astronomer.javasdk;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.airflow.sdk.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Builder.Dag(id = "java_task_syntax_example")
public class JavaEtlExample {
  private static final Logger logger = LoggerFactory.getLogger(JavaEtlExample.class);

  @Builder.Task(id = "transform")
  public Map<String, Object> transform(
      Client client, @Builder.XCom(task = "extract") Map<String, Object> payload) {
    logger.info("[transform/java] received payload from python 'extract' task: {}", payload);

    List<?> numbers = (List<?>) payload.get("numbers");
    long sum = 0;
    for (Object n : numbers) {
      sum += ((Number) n).longValue();
    }

    Map<String, Object> result = new LinkedHashMap<>();
    result.put("sum", sum);
    result.put("count", numbers.size());
    result.put("computed_by", "Java " + System.getProperty("java.version"));

    logger.info("[transform/java] summed {} numbers to {}", numbers.size(), sum);
    return result;
  }
}
