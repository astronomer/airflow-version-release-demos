package com.astronomer.javasdk;

import java.util.List;
import org.apache.airflow.sdk.*;

public class EtlBundleBuilder implements BundleBuilder {
  @Override
  public Iterable<Dag> getDags() {
    return List.of(JavaEtlExampleBuilder.build());
  }

  public static void main(String[] args) {
    var bundle = new EtlBundleBuilder().build();
    Server.create(args).serve(bundle);
  }
}
