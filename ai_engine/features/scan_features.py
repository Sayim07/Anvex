def calculate_port_fanout(destination_ports):
    """Count unique destination ports contacted."""
    return len(set(destination_ports))


def calculate_connection_failure_rate(failed_connections, total_connections):
    """Calculate the fraction of failed connections."""
    if total_connections <= 0:
        return 0.0

    return failed_connections / total_connections


def extract_scan_features(destination_ports, failed_connections, total_connections):
    """Extract Port Scan features."""

    return {
        "port_fanout": calculate_port_fanout(destination_ports),
        "connection_failure_rate": calculate_connection_failure_rate(
            failed_connections,
            total_connections,
        ),
    }