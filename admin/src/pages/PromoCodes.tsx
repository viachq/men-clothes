import { useEffect, useState } from 'react';
import api from '../api/client';
import { Tag, Plus, Percent, DollarSign, Edit, Power, PowerOff, Calendar, Hash, X } from 'lucide-react';

interface PromoCode {
  id: number;
  code: string;
  discount_percent: number | null;
  discount_amount: number | null;
  min_order_amount: number | null;
  max_uses: number | null;
  current_uses: number;
  is_active: boolean;
  valid_from: string | null;
  valid_until: string | null;
  created_at: string;
}

interface PromoFormData {
  code: string;
  discount_type: 'percent' | 'amount';
  discount_value: number;
  min_order_amount: number;
  max_uses: number;
  is_active: boolean;
  valid_from: string;
  valid_until: string;
}

const emptyForm: PromoFormData = {
  code: '',
  discount_type: 'percent',
  discount_value: 0,
  min_order_amount: 0,
  max_uses: 0,
  is_active: true,
  valid_from: '',
  valid_until: '',
};

export default function PromoCodes() {
  const [promos, setPromos] = useState<PromoCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPromo, setEditingPromo] = useState<PromoCode | null>(null);
  const [formData, setFormData] = useState<PromoFormData>(emptyForm);

  useEffect(() => {
    fetchPromos();
  }, []);

  const fetchPromos = async () => {
    try {
      const response = await api.get('/promo/');
      setPromos(response.data);
    } catch (error) {
      console.error('Failed to fetch promo codes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload: any = {
        code: formData.code,
        is_active: formData.is_active,
      };

      if (formData.discount_type === 'percent') {
        payload.discount_percent = formData.discount_value;
        payload.discount_amount = null;
      } else {
        payload.discount_amount = Math.round(formData.discount_value * 100);
        payload.discount_percent = null;
      }

      if (formData.min_order_amount > 0) {
        payload.min_order_amount = Math.round(formData.min_order_amount * 100);
      }
      if (formData.max_uses > 0) {
        payload.max_uses = formData.max_uses;
      }
      if (formData.valid_from) {
        payload.valid_from = formData.valid_from;
      }
      if (formData.valid_until) {
        payload.valid_until = formData.valid_until;
      }

      if (editingPromo) {
        await api.put(`/promo/${editingPromo.id}`, payload);
      } else {
        await api.post('/promo/', payload);
      }

      fetchPromos();
      closeModal();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не вдалося зберегти промокод');
    }
  };

  const toggleActive = async (promo: PromoCode) => {
    try {
      if (promo.is_active) {
        await api.delete(`/promo/${promo.id}`);
      } else {
        await api.put(`/promo/${promo.id}`, { is_active: true });
      }
      fetchPromos();
    } catch (error) {
      console.error('Failed to toggle promo status:', error);
    }
  };

  const openModal = (promo?: PromoCode) => {
    if (promo) {
      setEditingPromo(promo);
      setFormData({
        code: promo.code,
        discount_type: promo.discount_percent ? 'percent' : 'amount',
        discount_value: promo.discount_percent
          ? promo.discount_percent
          : promo.discount_amount
            ? promo.discount_amount / 100
            : 0,
        min_order_amount: promo.min_order_amount ? promo.min_order_amount / 100 : 0,
        max_uses: promo.max_uses || 0,
        is_active: promo.is_active,
        valid_from: promo.valid_from ? promo.valid_from.slice(0, 16) : '',
        valid_until: promo.valid_until ? promo.valid_until.slice(0, 16) : '',
      });
    } else {
      setEditingPromo(null);
      setFormData(emptyForm);
    }
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setEditingPromo(null);
    setFormData(emptyForm);
  };

  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-white"></div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b-2 border-neutral-200 dark:border-neutral-700 pb-4">
        <div className="flex items-center gap-3">
          <Tag className="w-6 h-6 text-neutral-900 dark:text-white" />
          <h1 className="text-2xl font-black text-neutral-900 dark:text-white tracking-tight uppercase">
            Промокоди
          </h1>
        </div>
        <button
          onClick={() => openModal()}
          className="inline-flex items-center gap-2 bg-neutral-900 dark:bg-white text-white dark:text-black px-5 py-2.5 rounded-lg hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors font-medium text-sm"
        >
          <Plus className="w-4 h-4" /> Створити промокод
        </button>
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-neutral-50 dark:bg-neutral-800 border-b-2 border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Код</span>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Знижка</span>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Мін. сума</span>
                </th>
                <th className="px-6 py-4 text-center">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Використання</span>
                </th>
                <th className="px-6 py-4 text-center">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Статус</span>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Дійсний</span>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">Дії</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
              {promos.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <Tag className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mb-4" />
                      <p className="text-neutral-500 dark:text-neutral-400 text-lg font-semibold">Промокодів не знайдено</p>
                      <p className="text-neutral-400 dark:text-neutral-500 text-sm mt-2">
                        Створіть перший промокод для ваших клієнтів
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                promos.map((promo) => (
                  <tr key={promo.id} className="hover:bg-neutral-50/50 dark:hover:bg-neutral-800/50 transition-all duration-150 group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <Hash className="w-4 h-4 text-neutral-400 dark:text-neutral-500" />
                        <span className="text-sm font-bold text-neutral-900 dark:text-white font-mono uppercase">
                          {promo.code}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        {promo.discount_percent ? (
                          <>
                            <Percent className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
                            <span className="text-base font-black text-neutral-900 dark:text-white">
                              {promo.discount_percent}%
                            </span>
                          </>
                        ) : (
                          <>
                            <DollarSign className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
                            <span className="text-base font-black text-neutral-900 dark:text-white">
                              ₴{((promo.discount_amount || 0) / 100).toFixed(2)}
                            </span>
                          </>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
                        {promo.min_order_amount
                          ? `₴${(promo.min_order_amount / 100).toFixed(2)}`
                          : '---'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      <span className="text-sm font-bold text-neutral-900 dark:text-white">
                        {promo.current_uses}
                      </span>
                      <span className="text-sm text-neutral-400 dark:text-neutral-500">
                        {' / '}
                        {promo.max_uses || '∞'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${
                          promo.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-neutral-100 text-neutral-500'
                        }`}
                      >
                        {promo.is_active ? 'Активний' : 'Неактивний'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col text-xs text-neutral-500 dark:text-neutral-400">
                        {promo.valid_from && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            з {new Date(promo.valid_from).toLocaleDateString('uk-UA')}
                          </span>
                        )}
                        {promo.valid_until && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            до {new Date(promo.valid_until).toLocaleDateString('uk-UA')}
                          </span>
                        )}
                        {!promo.valid_from && !promo.valid_until && (
                          <span className="text-neutral-400 dark:text-neutral-500">Безстроковий</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openModal(promo)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold text-neutral-700 dark:text-neutral-300 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-all duration-150"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => toggleActive(promo)}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold rounded-lg transition-all duration-150 ${
                            promo.is_active
                              ? 'text-red-600 hover:bg-red-50'
                              : 'text-green-600 hover:bg-green-50'
                          }`}
                          title={promo.is_active ? 'Деактивувати' : 'Активувати'}
                        >
                          {promo.is_active ? (
                            <PowerOff className="w-4 h-4" />
                          ) : (
                            <Power className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 py-8">
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={closeModal} />
            <div className="relative bg-white dark:bg-neutral-900 rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border-2 border-neutral-200 dark:border-neutral-700 max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="relative bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 px-8 py-6 sticky top-0 z-10">
                <div className="absolute top-0 left-0 right-0 h-1 bg-white/20"></div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                    <Tag className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-black text-white tracking-tight uppercase">
                    {editingPromo ? 'Редагувати промокод' : 'Новий промокод'}
                  </h2>
                </div>
                <p className="text-white/70 text-sm">Заповніть дані промокоду</p>
              </div>

              <form onSubmit={handleSubmit} className="p-8 space-y-5">
                {/* Code */}
                <div>
                  <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                    Код промокоду
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.code}
                    onChange={(e) =>
                      setFormData({ ...formData, code: e.target.value.toUpperCase() })
                    }
                    className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-mono font-bold text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500 uppercase"
                    placeholder="SPRING2024"
                  />
                </div>

                {/* Discount type toggle + value */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      Тип знижки
                    </label>
                    <div className="flex rounded-xl border-2 border-neutral-200 dark:border-neutral-700 overflow-hidden">
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, discount_type: 'percent' })}
                        className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold transition-all ${
                          formData.discount_type === 'percent'
                            ? 'bg-neutral-900 dark:bg-white text-white dark:text-black'
                            : 'bg-white dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700'
                        }`}
                      >
                        <Percent className="w-4 h-4" />
                        Відсоток
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, discount_type: 'amount' })}
                        className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-semibold transition-all ${
                          formData.discount_type === 'amount'
                            ? 'bg-neutral-900 dark:bg-white text-white dark:text-black'
                            : 'bg-white dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-700'
                        }`}
                      >
                        <DollarSign className="w-4 h-4" />
                        Фіксована (₴)
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      {formData.discount_type === 'percent' ? 'Відсоток знижки' : 'Сума знижки (₴)'}
                    </label>
                    <input
                      type="number"
                      required
                      min={0}
                      max={formData.discount_type === 'percent' ? 100 : undefined}
                      step={formData.discount_type === 'percent' ? 1 : 0.01}
                      value={formData.discount_value || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, discount_value: Number(e.target.value) })
                      }
                      className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500"
                      placeholder={formData.discount_type === 'percent' ? '10' : '100.00'}
                    />
                  </div>
                </div>

                {/* Min order amount + Max uses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      Мін. сума замовлення (₴)
                    </label>
                    <input
                      type="number"
                      min={0}
                      step={0.01}
                      value={formData.min_order_amount || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, min_order_amount: Number(e.target.value) })
                      }
                      className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500"
                      placeholder="0 = без обмежень"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      Макс. використань
                    </label>
                    <input
                      type="number"
                      min={0}
                      value={formData.max_uses || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, max_uses: Number(e.target.value) })
                      }
                      className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-neutral-500"
                      placeholder="0 = необмежено"
                    />
                  </div>
                </div>

                {/* Valid from/until */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      Дійсний з
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.valid_from}
                      onChange={(e) =>
                        setFormData({ ...formData, valid_from: e.target.value })
                      }
                      className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
                      Дійсний до
                    </label>
                    <input
                      type="datetime-local"
                      value={formData.valid_until}
                      onChange={(e) =>
                        setFormData({ ...formData, valid_until: e.target.value })
                      }
                      className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white"
                    />
                  </div>
                </div>

                {/* Buttons */}
                <div className="flex gap-3 pt-4 border-t border-neutral-100 dark:border-neutral-800">
                  <button
                    type="button"
                    onClick={closeModal}
                    className="flex-1 py-3.5 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 rounded-xl hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors font-semibold text-sm"
                  >
                    Скасувати
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-3.5 bg-gradient-to-r from-neutral-900 to-neutral-800 text-white rounded-xl hover:from-neutral-800 hover:to-neutral-700 transition-all font-semibold text-sm shadow-lg"
                  >
                    Зберегти
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
