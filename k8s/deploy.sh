#!/bin/bash
# Скрипт для швидкого деплою всіх Kubernetes ресурсів

set -e

echo "🚀 Deploying Men's Clothes Store Microservices to Kubernetes..."

# Перевірка чи kubectl доступний
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не знайдено. Встановіть kubectl спочатку."
    exit 1
fi

# Створити namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Застосувати ConfigMap та Secret
echo "🔧 Applying ConfigMap and Secret..."
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# Застосувати backend сервіси
echo "🔨 Deploying backend services..."
kubectl apply -f auth-service/
kubectl apply -f catalog-service/
kubectl apply -f order-service/

# Застосувати frontend сервіси
echo "🎨 Deploying frontend services..."
kubectl apply -f client-frontend/
kubectl apply -f admin-frontend/

# Застосувати Ingress (якщо потрібно)
if [ "$1" == "--with-ingress" ]; then
    echo "🌐 Applying Ingress..."
    kubectl apply -f ingress.yaml
fi

# Чекати поки pods стануть готовими
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=auth-service -n ippt-microservices --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=catalog-service -n ippt-microservices --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=order-service -n ippt-microservices --timeout=120s || true

# Показати статус
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Status:"
kubectl get pods -n ippt-microservices
echo ""
echo "🔗 Services:"
kubectl get svc -n ippt-microservices
echo ""
echo "💡 To access services, use port-forwarding:"
echo "   kubectl port-forward svc/auth-service 8001:8001 -n ippt-microservices"
echo "   kubectl port-forward svc/catalog-service 8002:8002 -n ippt-microservices"
echo "   kubectl port-forward svc/order-service 8003:8003 -n ippt-microservices"
echo "   kubectl port-forward svc/client-frontend 5174:5174 -n ippt-microservices"
echo "   kubectl port-forward svc/admin-frontend 5173:5173 -n ippt-microservices"
