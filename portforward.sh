
#!/usr/bin/env bash
set -euo pipefail
ns=${1:-monitoring}
echo "Forwarding Grafana(3000), Prometheus(9090), Loki(3100), Tempo(3200), Icinga(8080)..."
kubectl -n "$ns" port-forward svc/grafana 3000:3000 &
kubectl -n "$ns" port-forward svc/kps-kube-prometheus 9090:9090 &
kubectl -n "$ns" port-forward svc/loki 3100:3100 &
kubectl -n "$ns" port-forward svc/tempo 3200:3100 &
kubectl -n "$ns" port-forward svc/icinga 8080:80 &
wait
