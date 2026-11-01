/**
 * Type-safe Edge Cluster Definitions.
 */

export interface ClusterNode {
    id: string;
    hostname: string;
    ipAddress: string;
    cores: number;
    memoryMb: number;
    isActive: boolean;
    tags: string[];
}

export type HealthStatus = "HEALTHY" | "DEGRADED" | "CRITICAL" | "OFFLINE";

export function evaluateClusterHealth(nodes: ClusterNode[]): HealthStatus {
    const activeNodes = nodes.filter(n => n.isActive);
    const healthRatio = activeNodes.length / nodes.length;

    if (healthRatio >= 0.95) return "HEALTHY";
    if (healthRatio >= 0.70) return "DEGRADED";
    if (healthRatio > 0.0) return "CRITICAL";
    return "OFFLINE";
}
