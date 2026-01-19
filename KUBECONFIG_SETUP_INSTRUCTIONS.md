# Інструкція: Налаштування KUBECONFIG для GitHub Actions

## ✅ Файли створено:

1. **kubeconfig-minikube-clean.txt** - чистий kubeconfig файл тільки для minikube
2. **kubeconfig-base64.txt** - base64 закодований kubeconfig (готовий для GitHub Secrets)

## ⚠️ ВАЖЛИВО: Обмеження локального minikube

**Локальний minikube на Windows НЕ ПРАЦЮВАТИМЕ з GitHub Actions** з наступних причин:

1. GitHub Actions запускається на GitHub серверах, а не на вашому комп'ютері
2. minikube IP (192.168.49.2) - це локальна адреса, недоступна з інтернету
3. Потрібен публічний кластер (GKE, EKS, AKS) або minikube на VPS сервері

## 🎯 Що робити далі:

### Варіант 1: Cloud кластер (рекомендовано)

Використовуйте публічний Kubernetes кластер:
- **Google Kubernetes Engine (GKE)** - безкоштовний trial
- **Amazon EKS**
- **Azure AKS**

### Варіант 2: Minikube на VPS

Якщо маєте VPS сервер:
1. Встановіть minikube на VPS
2. Налаштуйте firewall для доступу до Kubernetes API
3. Використовуйте публічний IP VPS замість локального

## 📋 Як додати в GitHub Secrets (якщо маєте публічний кластер):

1. Перейдіть в GitHub репозиторій: **Settings** → **Secrets and variables** → **Actions**
2. Натисніть **New repository secret**
3. **Name**: `KUBECONFIG`
4. **Secret**: Скопіюйте вміст файлу `kubeconfig-base64.txt`
5. Натисніть **Add secret**

## 🔍 Перевірка:

Після додавання secret, наступний push в `main` автоматично:
- ✅ Збере образ
- ✅ Запушить в registry  
- 🚀 Задеплоїть в Kubernetes (якщо KUBECONFIG налаштовано)

## 📝 Поточна ситуація:

Наразі маємо локальний minikube, тому автоматичний деплой працюватиме тільки якщо:
- minikube запущений на публічному сервері (VPS)
- або використовується cloud кластер

**Pipeline все одно працює** - образи збираються та пушаться в registry, але деплой пропускається.
