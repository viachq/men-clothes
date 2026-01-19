# Kubernetes Deployment Setup Guide

Цей документ описує як налаштувати автоматичний деплой в Kubernetes через GitHub Actions.

## Вимоги

1. **Kubernetes кластер** (minikube, k3s, kind, або cloud кластер)
2. **kubectl** встановлений та налаштований локально
3. **GitHub репозиторій** з CI/CD pipeline

## Варіанти налаштування

### Варіант 1: Локальний кластер (minikube/k3s/kind)

#### Для minikube:

```bash
# Запустити minikube
minikube start

# Отримати kubeconfig
kubectl config view --flatten > kubeconfig.txt

# Завантажити як secret в GitHub
# Назва secret: KUBECONFIG
# Значення: вміст kubeconfig.txt (base64 encoded)
```

#### Для k3s:

```bash
# Отримати kubeconfig
sudo cat /etc/rancher/k3s/k3s.yaml > kubeconfig.txt

# Замінити localhost на IP сервера
sed -i 's/127.0.0.1/YOUR_SERVER_IP/g' kubeconfig.txt

# Завантажити як secret в GitHub
```

### Варіант 2: Cloud кластер (GKE, EKS, AKS)

#### Google Kubernetes Engine (GKE):

```bash
# Отримати credentials
gcloud container clusters get-credentials CLUSTER_NAME --zone=ZONE --project=PROJECT_ID

# Експортувати kubeconfig
kubectl config view --flatten > kubeconfig.txt

# Завантажити як secret в GitHub
```

#### Amazon EKS:

```bash
# Отримати credentials
aws eks update-kubeconfig --name CLUSTER_NAME --region REGION

# Експортувати kubeconfig
kubectl config view --flatten > kubeconfig.txt

# Завантажити як secret в GitHub
```

#### Azure Kubernetes Service (AKS):

```bash
# Отримати credentials
az aks get-credentials --resource-group RESOURCE_GROUP --name CLUSTER_NAME

# Експортувати kubeconfig
kubectl config view --flatten > kubeconfig.txt

# Завантажити як secret в GitHub
```

## Налаштування GitHub Secret

1. Перейти в **Settings** → **Secrets and variables** → **Actions**
2. Натиснути **New repository secret**
3. Назва: `KUBECONFIG`
4. Значення: вміст `kubeconfig.txt` закодований в base64:

```bash
# Linux/Mac
cat kubeconfig.txt | base64 -w 0

# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("kubeconfig.txt"))
```

5. Натиснути **Add secret**

## Налаштування Registry Permissions

GitHub Container Registry (ghcr.io) автоматично налаштований через `GITHUB_TOKEN`.

Якщо використовуєте інший registry:

1. Створити secret `REGISTRY_USERNAME`
2. Створити secret `REGISTRY_PASSWORD`
3. Оновити `.github/workflows/ci-cd.yml`:

```yaml
- name: Log in to Container Registry
  uses: docker/login-action@v3
  with:
    registry: your-registry.com
    username: ${{ secrets.REGISTRY_USERNAME }}
    password: ${{ secrets.REGISTRY_PASSWORD }}
```

## Налаштування Kubernetes Namespace

Namespace `food-delivery` створюється автоматично через `k8s/namespace.yaml`.

Якщо потрібен інший namespace, змініть у всіх манифестах:

```bash
# Замінити namespace в усіх файлах
sed -i 's/namespace: food-delivery/namespace: your-namespace/g' k8s/**/*.yaml
```

## Перевірка деплою

Після push до `main` гілки:

1. Перевірити GitHub Actions → **CI/CD Pipeline**
2. Подивитися логи job **deploy**
3. Якщо все добре, перевірити в кластері:

```bash
kubectl get pods -n food-delivery
kubectl get deployments -n food-delivery
kubectl get svc -n food-delivery
```

## Troubleshooting

### Помилка: "KUBECONFIG secret not found"

**Рішення**: Додайте secret `KUBECONFIG` в GitHub Settings → Secrets → Actions

### Помилка: "Unable to connect to the server"

**Рішення**: 
- Перевірте що kubeconfig правильний
- Для minikube: переконайтеся що кластер запущений
- Для cloud: перевірте firewall та network settings

### Помилка: "ImagePullBackOff"

**Рішення**:
- Перевірте що образи зібрані та завантажені в registry
- Перевірте права доступу до registry
- Перевірте image names в deployment.yaml

### Помилка: "Forbidden" при деплої

**Рішення**:
- Перевірте права користувача в kubeconfig
- Переконайтеся що маєте права на namespace
- Можливо потрібно створити ServiceAccount:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: github-actions
  namespace: food-delivery
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: github-actions-binding
  namespace: food-delivery
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: github-actions
  namespace: food-delivery
```

## Відключення автоматичного деплою

Якщо не хочете автоматичний деплой, просто не додавайте secret `KUBECONFIG`.

Pipeline все одно буде збирати та пушити образи, але пропустить крок деплою.

## Ручний деплой

Якщо автоматичний деплой не працює, можна зробити вручну:

```bash
# Оновити image tags
export IMAGE_TAG="latest"
export IMAGE_PREFIX="ghcr.io/viachq/ippt-microservices"

sed -i "s|image:.*auth-service.*|image: ${IMAGE_PREFIX}-auth-service:${IMAGE_TAG}|g" k8s/auth-service/deployment.yaml
# ... (для інших сервісів)

# Застосувати
kubectl apply -f k8s/
```

Або використати готові скрипти:

```bash
# Linux/Mac
cd k8s && ./deploy.sh --with-ingress

# Windows
cd k8s && deploy.bat --with-ingress
```
