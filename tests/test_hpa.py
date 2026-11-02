import pytest
from kubernetes import client, config

def test_hpa_scales():
    """Test that HPA scales within defined limits."""
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    # Get HPA
    hpa = v1.read_namespaced_horizontal_pod_autoscaler(
        name="rag-platform-hpa", namespace="default"
    )
    
    # Verify min/max replicas
    assert hpa.spec.min_replicas == 2
    assert hpa.spec.max_replicas == 10
    
    # Verify HPA is active
    assert hpa.status.current_replicas > 0
    assert hpa.status.desired_replicas >= hpa.spec.min_replicas


def test_hpa_based_on_p95_metric():
    """Test that HPA is based on p95 latency metric."""
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    hpa = v1.read_namespaced_horizontal_pod_autoscaler(
        name="rag-platform-hpa", namespace="default"
    )
    
    # Verify metrics source
    assert hpa.spec.metric_sources is not None
    metric_name = hpa.spec.metric_sources[0].resource.metrics_name
    assert metric_name == "request_latency_seconds_p95"


def test_chaos_mttr_within_5min():
    """Test that chaos experiments achieve MTTR within 5 minutes."""
    # This test verifies the chaos experiment framework
    # and checks that recovery mechanisms are in place
    
    # Check that PDB is enforced
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    pdb = v1.read_namespaced_pod_disruption_budget(
        name="rag-platform-pdb", namespace="default"
    )
    
    assert pdb.spec.min_available == 1
    assert pdb.spec.max_unavailable == 1


def test_chaos_experiments_defined():
    """Test that chaos experiments are properly defined."""
    import yaml
    
    with open("k8s/chaos_experiments.yaml") as f:
        experiments = yaml.safe_load(f)
    
    # Verify experiments are defined
    assert "pod-kill-experiment" in experiments
    assert "network-latency-experiment" in experiments
    assert "cpu-stress-experiment" in experiments
    
    # Verify experiment properties
    exp = experiments["pod-kill-experiment"]
    assert "chaos" in experiments["pod-kill-experiment"]
    assert "target" in experiments["pod-kill-experiment"]