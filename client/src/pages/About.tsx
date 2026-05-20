import { Award, Users, Clock, Shield, Truck, CreditCard } from 'lucide-react';

const values = [
  {
    icon: Award,
    title: 'Якість',
    description: 'Ми ретельно відбираємо кожну позицію, щоб забезпечити найвищу якість тканин та пошиву.',
  },
  {
    icon: Shield,
    title: 'Стиль',
    description: 'Сучасні колекції, що поєднують класику та тренди — для чоловіків, які цінують свій образ.',
  },
  {
    icon: CreditCard,
    title: 'Доступність',
    description: 'Справедливі ціни без компромісів. Стильний одяг не повинен коштувати цілий стан.',
  },
  {
    icon: Truck,
    title: 'Швидка доставка',
    description: 'Оперативна доставка по всій Україні. Ваше замовлення буде у вас якнайшвидше.',
  },
];

const stats = [
  { value: '1000+', label: 'Товарів у каталозі' },
  { value: '5000+', label: 'Задоволених клієнтів' },
  { value: '3+', label: 'Роки досвіду' },
];

export default function About() {
  return (
    <div className="max-w-6xl mx-auto p-4 md:p-8">
      {/* Hero Section */}
      <div className="text-center py-12 md:py-20">
        <h1 className="text-3xl md:text-4xl font-bold text-neutral-900 dark:text-white mb-4 uppercase tracking-wide">
          Про нас
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          Men's Clothes — це український інтернет-магазин чоловічого одягу, створений з пристрастю до стилю та якості.
          Ми віримо, що кожен чоловік заслуговує на одяг, який підкреслює його індивідуальність.
        </p>
      </div>

      {/* Mission Section */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 md:p-10 mb-10">
        <div className="flex items-center gap-3 mb-4">
          <Clock className="w-6 h-6 text-neutral-900 dark:text-white" />
          <h2 className="text-xl md:text-2xl font-bold text-neutral-900 dark:text-white uppercase tracking-wide">
            Наша місія
          </h2>
        </div>
        <p className="text-neutral-600 dark:text-neutral-400 text-sm md:text-base leading-relaxed">
          Ми прагнемо зробити якісний чоловічий одяг доступним для кожного українця. Наша команда щодня працює над тим,
          щоб розширити асортимент, знайти найкращих постачальників та забезпечити бездоганний сервіс. Від повсякденного
          стилю до ділового дрес-коду — у нас є все, що потрібно сучасному чоловікові.
        </p>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6 mb-10">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 text-center"
          >
            <p className="text-3xl md:text-4xl font-black text-neutral-900 dark:text-white mb-2">
              {stat.value}
            </p>
            <p className="text-neutral-600 dark:text-neutral-400 text-sm font-medium">
              {stat.label}
            </p>
          </div>
        ))}
      </div>

      {/* Values Section */}
      <div className="mb-10">
        <h2 className="text-xl md:text-2xl font-bold text-neutral-900 dark:text-white mb-6 uppercase tracking-wide text-center">
          Наші цінності
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
          {values.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.title}
                className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-neutral-900 dark:text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                    {item.title}
                  </h3>
                </div>
                <p className="text-neutral-600 dark:text-neutral-400 text-sm leading-relaxed">
                  {item.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Team / Why Us Section */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 md:p-10">
        <div className="flex items-center gap-3 mb-4">
          <Users className="w-6 h-6 text-neutral-900 dark:text-white" />
          <h2 className="text-xl md:text-2xl font-bold text-neutral-900 dark:text-white uppercase tracking-wide">
            Чому обирають нас
          </h2>
        </div>
        <ul className="space-y-3 text-neutral-600 dark:text-neutral-400 text-sm md:text-base leading-relaxed">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-900 dark:bg-white mt-2 flex-shrink-0" />
            Широкий асортимент — від футболок до класичних костюмів
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-900 dark:bg-white mt-2 flex-shrink-0" />
            Тільки перевірені бренди та матеріали
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-900 dark:bg-white mt-2 flex-shrink-0" />
            Зручна доставка Новою Поштою та Укрпоштою по всій Україні
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-900 dark:bg-white mt-2 flex-shrink-0" />
            Професійна підтримка клієнтів 7 днів на тиждень
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-neutral-900 dark:bg-white mt-2 flex-shrink-0" />
            Безкоштовне повернення протягом 14 днів
          </li>
        </ul>
      </div>
    </div>
  );
}
