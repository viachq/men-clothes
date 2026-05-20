import { useState } from 'react';
import { Phone, Mail, MapPin, Clock, Send } from 'lucide-react';
import { showSuccess } from '../utils/notifications';

const contactInfo = [
  {
    icon: Phone,
    label: 'Телефон',
    value: '+380 (50) 123-45-67',
    href: 'tel:+380501234567',
  },
  {
    icon: Mail,
    label: 'Email',
    value: 'info@mensclothes.ua',
    href: 'mailto:info@mensclothes.ua',
  },
  {
    icon: MapPin,
    label: 'Адреса',
    value: 'м. Київ, вул. Хрещатик, 22',
    href: null,
  },
];

const workingHours = [
  { days: 'Пн-Пт', hours: '09:00 - 21:00' },
  { days: 'Сб-Нд', hours: '10:00 - 20:00' },
];

export default function Contacts() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);

    // Simulate form submission
    setTimeout(() => {
      showSuccess('Дякуємо! Ваше повідомлення успішно надіслано. Ми зв\'яжемося з вами найближчим часом.');
      setName('');
      setEmail('');
      setMessage('');
      setSending(false);
    }, 800);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      {/* Header */}
      <div className="text-center py-12 md:py-20">
        <h1 className="text-3xl md:text-4xl font-bold text-neutral-900 dark:text-white mb-4 uppercase tracking-wide">
          Контакти
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          Маєте запитання? Зв'яжіться з нами будь-яким зручним способом або залиште повідомлення через форму нижче.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-10">
        {/* Left Column - Contact Info */}
        <div className="space-y-6">
          {/* Contact Details */}
          <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
            <h2 className="text-lg md:text-xl font-bold text-neutral-900 dark:text-white mb-5 uppercase tracking-wide">
              Як нас знайти
            </h2>
            <div className="space-y-5">
              {contactInfo.map((item) => {
                const Icon = item.icon;
                const content = (
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5 text-neutral-900 dark:text-white" />
                    </div>
                    <div>
                      <p className="text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wide mb-1">
                        {item.label}
                      </p>
                      <p className="text-sm font-semibold text-neutral-900 dark:text-white">
                        {item.value}
                      </p>
                    </div>
                  </div>
                );

                return item.href ? (
                  <a
                    key={item.label}
                    href={item.href}
                    className="block hover:bg-neutral-50 dark:hover:bg-neutral-800 -mx-3 px-3 py-2 rounded-lg transition-colors"
                  >
                    {content}
                  </a>
                ) : (
                  <div key={item.label} className="py-2">
                    {content}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Working Hours */}
          <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
            <div className="flex items-center gap-3 mb-5">
              <Clock className="w-5 h-5 text-neutral-900 dark:text-white" />
              <h2 className="text-lg md:text-xl font-bold text-neutral-900 dark:text-white uppercase tracking-wide">
                Графік роботи
              </h2>
            </div>
            <div className="space-y-3">
              {workingHours.map((item) => (
                <div
                  key={item.days}
                  className="flex items-center justify-between py-2 border-b border-neutral-100 dark:border-neutral-800 last:border-0"
                >
                  <span className="text-sm font-medium text-neutral-900 dark:text-white">
                    {item.days}
                  </span>
                  <span className="text-sm text-neutral-600 dark:text-neutral-400 font-medium">
                    {item.hours}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Contact Form */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
          <h2 className="text-lg md:text-xl font-bold text-neutral-900 dark:text-white mb-5 uppercase tracking-wide">
            Написати нам
          </h2>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name */}
            <div>
              <label
                htmlFor="contact-name"
                className="block text-xs font-bold text-neutral-900 dark:text-white mb-2 uppercase tracking-wider"
              >
                Ваше ім'я
              </label>
              <input
                id="contact-name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Введіть ваше ім'я"
                className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent outline-none transition-all"
              />
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="contact-email"
                className="block text-xs font-bold text-neutral-900 dark:text-white mb-2 uppercase tracking-wider"
              >
                Email
              </label>
              <input
                id="contact-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent outline-none transition-all"
              />
            </div>

            {/* Message */}
            <div>
              <label
                htmlFor="contact-message"
                className="block text-xs font-bold text-neutral-900 dark:text-white mb-2 uppercase tracking-wider"
              >
                Повідомлення
              </label>
              <textarea
                id="contact-message"
                required
                rows={5}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Напишіть ваше повідомлення..."
                className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent outline-none transition-all resize-none"
              />
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={sending}
              className="w-full flex items-center justify-center gap-2 bg-neutral-900 dark:bg-white text-white dark:text-black px-6 py-3 text-sm font-bold uppercase tracking-wider hover:bg-black dark:hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-lg"
            >
              <Send className="w-4 h-4" />
              {sending ? 'Надсилання...' : 'Надіслати'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
