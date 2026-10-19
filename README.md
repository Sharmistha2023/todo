# Todo Helm repository

```sh
helm repo add todo https://sharmistha2023.github.io/todo
helm repo update
helm install todo todo/todo --set postgres.db_url=postgresql://USER:PASS@HOST:5432/DB
```

Chart source: the `main` branch, `charts/todo/`.
