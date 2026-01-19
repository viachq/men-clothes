/**
 * Сучасна система сповіщень (Toast Notifications)
 * Унікальний дизайн для Men's Clothes
 */

export type NotificationType = 'success' | 'error' | 'info' | 'warning';

export interface NotificationOptions {
  message: string;
  type?: NotificationType;
  duration?: number;
}

// Створюємо контейнер для сповіщень якщо його немає
const getNotificationContainer = (): HTMLElement => {
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }
  return container;
};

export const showNotification = (
  message: string,
  type: NotificationType = 'success',
  duration: number = 4000
) => {
  const container = getNotificationContainer();
  
  // Створюємо унікальний ID для сповіщення
  const notificationId = `notification-${Date.now()}-${Math.random()}`;
  
  // Кольори та стилі для кожного типу
  const styles: Record<NotificationType, { bg: string; border: string; icon: string; iconBg: string }> = {
    success: {
      bg: '#ffffff',
      border: '#10b981',
      icon: '#10b981',
      iconBg: '#d1fae5',
    },
    error: {
      bg: '#ffffff',
      border: '#ef4444',
      icon: '#ef4444',
      iconBg: '#fee2e2',
    },
    info: {
      bg: '#ffffff',
      border: '#3b82f6',
      icon: '#3b82f6',
      iconBg: '#dbeafe',
    },
    warning: {
      bg: '#ffffff',
      border: '#f59e0b',
      icon: '#f59e0b',
      iconBg: '#fef3c7',
    },
  };

  const style = styles[type];

  // Іконки для кожного типу
  const icons: Record<NotificationType, string> = {
    success: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16.7071 5.29289C17.0976 5.68342 17.0976 6.31658 16.7071 6.70711L8.70711 14.7071C8.31658 15.0976 7.68342 15.0976 7.29289 14.7071L3.29289 10.7071C2.90237 10.3166 2.90237 9.68342 3.29289 9.29289C3.68342 8.90237 4.31658 8.90237 4.70711 9.29289L8 12.5858L15.2929 5.29289C15.6834 4.90237 16.3166 4.90237 16.7071 5.29289Z" fill="${style.icon}"/>
    </svg>`,
    error: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z" fill="${style.icon}"/>
      <path d="M10 11L13 8M13 11L10 8" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    info: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z" fill="${style.icon}"/>
      <path d="M10 6V10M10 14H10.01" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    warning: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M10 2L2 18H18L10 2Z" fill="${style.icon}"/>
      <path d="M10 8V12M10 16H10.01" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
  };

  // Створюємо елемент сповіщення
  const notification = document.createElement('div');
  notification.id = notificationId;
  notification.style.cssText = `
    background: ${style.bg};
    border-left: 4px solid ${style.border};
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 320px;
    max-width: 420px;
    pointer-events: auto;
    animation: slideInRight 0.3s ease-out;
    transform: translateX(400px);
    opacity: 0;
  `;

  // Додаємо анімацію
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    @keyframes slideInRight {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOutRight {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  if (!document.getElementById('notification-styles')) {
    styleSheet.id = 'notification-styles';
    document.head.appendChild(styleSheet);
  }

  // Іконка
  const iconContainer = document.createElement('div');
  iconContainer.style.cssText = `
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: ${style.iconBg};
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  `;
  iconContainer.innerHTML = icons[type];

  // Текст
  const textContainer = document.createElement('div');
  textContainer.style.cssText = `
    flex: 1;
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
    line-height: 1.5;
  `;
  textContainer.textContent = message;

  // Кнопка закриття
  const closeButton = document.createElement('button');
  closeButton.style.cssText = `
    width: 24px;
    height: 24px;
    border: none;
    background: transparent;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    color: #6b7280;
    transition: color 0.2s;
  `;
  closeButton.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 4L4 12M4 4L12 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
    </svg>
  `;
  closeButton.onmouseenter = () => {
    closeButton.style.color = '#1f2937';
  };
  closeButton.onmouseleave = () => {
    closeButton.style.color = '#6b7280';
  };

  const removeNotification = () => {
    notification.style.animation = 'slideOutRight 0.3s ease-out';
    notification.style.transform = 'translateX(400px)';
    notification.style.opacity = '0';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  };

  closeButton.onclick = removeNotification;

  notification.appendChild(iconContainer);
  notification.appendChild(textContainer);
  notification.appendChild(closeButton);
  container.appendChild(notification);

  // Анімація появи
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
    notification.style.opacity = '1';
    notification.style.transition = 'all 0.3s ease-out';
  }, 10);

  // Автоматичне видалення
  const timeoutId = setTimeout(removeNotification, duration);

  // Зупиняємо таймер при наведенні
  notification.onmouseenter = () => {
    clearTimeout(timeoutId);
  };
  notification.onmouseleave = () => {
    const newTimeoutId = setTimeout(removeNotification, duration);
    (notification as any).timeoutId = newTimeoutId;
  };
};

// Зручні обгортки для різних типів
export const showSuccess = (message: string, duration?: number) =>
  showNotification(message, 'success', duration);

export const showError = (message: string, duration?: number) =>
  showNotification(message, 'error', duration);

export const showInfo = (message: string, duration?: number) =>
  showNotification(message, 'info', duration);

export const showWarning = (message: string, duration?: number) =>
  showNotification(message, 'warning', duration);
