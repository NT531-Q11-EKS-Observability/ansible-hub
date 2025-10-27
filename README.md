
# Observability for EKS (Final, Ready-to-Demo)

Triển khai Prometheus + Grafana + Alertmanager + Loki + Promtail + Tempo + Icinga2
lên EKS (2 nodes), **không cần StorageClass** (ephemeral). Phù hợp cho demo và
các kịch bản: autoscaling, chaos/outage, latency.

## Yêu cầu
- `kubectl`, `helm`, `ansible`
- `ansible-galaxy collection install kubernetes.core`
- Kubeconfig đang trỏ vào EKS (`~/.kube/config`)

## Deploy
```bash
ansible-playbook -i inventory.ini playbook.yml
kubectl get pods -n monitoring
```

## Port-forward nhanh
```bash
kubectl -n monitoring port-forward svc/grafana 3000:3000
kubectl -n monitoring port-forward svc/kps-kube-prometheus 9090:9090
kubectl -n monitoring port-forward svc/loki 3100:3100
kubectl -n monitoring port-forward svc/tempo 3200:3100
kubectl -n monitoring port-forward svc/icinga 8080:80
```

- Grafana: `http://localhost:3000` (admin / admin123)
- Icinga:  `http://localhost:8080` (icingaadmin / icinga123)

## Kịch bản test
1. **Autoscaling / Load**: apply `manifests/hpa-examples.yaml`, chạy Job k6 (`manifests/k6-job.yaml` được apply sẵn nếu bật). Quan sát p95 latency, error rate.
2. **Outage / Chaos**: dùng cordon/drain 1 node (hoặc tự dùng công cụ chaos của bạn) → quan sát pod reschedule & alert.
3. **East-West Latency**: tạo traffic nội bộ giữa các service của app (sửa TARGET_URL trong k6 Job nếu cần), theo dõi trace trên Tempo + logs Loki + metrics Prometheus.

> Lưu ý: Dữ liệu là **ephemeral** (emptyDir) để demo nhanh.
