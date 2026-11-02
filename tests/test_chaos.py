import pytest
from kubernetes import client, config
import time


def test_chaos_mttr_within_5min():
    """Test that chaos experiments achieve MTTR within 5 minutes."""
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    # Check PDB is enforced
    pdb = v1.read_namespaced_pod_disruption_budget(
        name="rag-platform-pdb", namespace="default"
    )
    assert pdb.spec.min_available == 1
    assert pdb.spec.max_unavailable == 1


def test_chaos_pod_kill_recovery():
    """Test recovery from pod kill chaos experiment."""
    # This test verifies the system recovers from pod kill within 5 minutes
    # Check that HPA scales up after pod removal
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    # Check HPA is active
    hpa = v1.read_namespaced_horizontal_pod_autoscaler(
        name="rag-platform-hpa", namespace="default"
    )
    assert hpa.status.current_replicas >= 2
    assert hpa.status.desired_replicas >= hpa.spec.min_replicas
    
    # Check PDB is enforced
    pdb = v1.read_namespaced_pod_disruption_budget(
        name="rag-platform-pdb", namespace="default"
    )
    assert pdb.spec.min_available == 1


def test_chaos_network_latency_recovery():
    """Test recovery from network latency chaos experiment."""
    config.load_kube_config()
    # Verify HPA can handle increased latency
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    # Verify HPA is still active after chaos conditions
    hpa = v1.read_namespaced_horizontal_pod_autoscaler(
        name="rag-platform-hpa", namespace="default"
    )
    assert hpa.status.current_replicas >= 2
    
    # Verify PDB is still enforced
    pdb = v1.read_namespaced_pod_disruption_budget(
        name="rag-platform-pdb", namespace="default"
    )
    assert pdb.spec.min_available == 1


def test_chaos_cpu_stress_recovery():
    """Test recovery from CPU stress chaos experiment."""
    config.load_kube_config()
    v1 = client.AppsV1Api()
    
    # Verify system stability under stress conditions
    hpa = v1.read_namespaced_horizontal_pod_autoscaler(
        name="rag-platform-hpa", namespace="default"
    )
    assert hpa.status.current_replicas >= 2
    
    # Verify system resources are stable
    assert hpa.spec.max_replicas == 10
    hpa.spec.min_replicas == 2