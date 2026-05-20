import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import type { CartItem, MenuItem, PromoValidateResponse } from '../types';
import { ShoppingCart, Trash2, Plus, Minus, ArrowRight, ArrowLeft, MapPin, Loader2, Tag, X, Check, UserIcon, Truck, MessageSquare } from 'lucide-react';
import { showSuccess, showError } from '../utils/notifications';

interface CartItemWithDetails extends CartItem {
  menu_item: MenuItem;
}

function LiqPayForm({ 
  data, 
  signature,
  orderId 
}: { 
  data: string
  signature: string
  orderId: number
}) {
  const formRef = useRef<HTMLFormElement>(null);
  const submittedRef = useRef(false);
  
  useEffect(() => {
    // Запобігаємо подвійній відправці через React StrictMode
    if (submittedRef.current) {
      console.log('LiqPayForm: Already submitted, skipping');
      return;
    }
    
    console.log('LiqPayForm: Component mounted with data:', data?.substring(0, 50), 'signature:', signature?.substring(0, 50));
    
    if (!data || !signature) {
      console.error('LiqPayForm: Missing data or signature', { data: !!data, signature: !!signature });
      return;
    }
    
    // Невелика затримка для впевненості, що форма відрендерилась
    const timeoutId = setTimeout(() => {
      if (submittedRef.current) {
        return;
      }
      
      submittedRef.current = true;
      console.log('LiqPayForm: Submitting form...');
      
      if (formRef.current) {
        try {
          console.log('LiqPayForm: Calling form.submit()', {
            action: formRef.current.action,
            method: formRef.current.method,
            hasData: !!data,
            hasSignature: !!signature
          });
          formRef.current.submit();
          console.log('LiqPayForm: Form submitted successfully');
        } catch (error) {
          console.error('LiqPayForm: Error submitting form:', error);
          submittedRef.current = false;
        }
      } else {
        console.error('LiqPayForm: Form ref is null');
        submittedRef.current = false;
      }
    }, 500);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [data, signature]);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 p-6">
        <div className="mb-4 flex items-center justify-between text-base">
          <span className="text-neutral-600 dark:text-neutral-400">Замовлення #{orderId}</span>
        </div>
      </div>

      <form
        ref={formRef}
        method="POST"
        action="https://www.liqpay.ua/api/3/checkout"
        target="_self"
        style={{ display: 'none' }}
      >
        <input type="hidden" name="data" value={data} />
        <input type="hidden" name="signature" value={signature} />
      </form>

      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-2 border-neutral-300 dark:border-neutral-600 border-t-neutral-900 dark:border-t-white mx-auto" />
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Перенаправлення на сторінку оплати LiqPay...</p>
        </div>
      </div>
    </div>
  );
}

export default function Cart() {
  const [cartItems, setCartItems] = useState<CartItemWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingItems, setRemovingItems] = useState<Set<number>>(new Set());
  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [address, setAddress] = useState('');
  const [deliveryMethod, setDeliveryMethod] = useState('nova_poshta');
  const [comment, setComment] = useState('');
  const [processingOrder, setProcessingOrder] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [paymentData, setPaymentData] = useState<{ data: string; signature: string; orderId: number } | null>(null);
  const [promoCode, setPromoCode] = useState('');
  const [promoResult, setPromoResult] = useState<PromoValidateResponse | null>(null);
  const [promoLoading, setPromoLoading] = useState(false);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    if (!localStorage.getItem('client_token')) {
      navigate('/');
      return;
    }
    fetchCart();

    // Перевіряємо чи повернулись з LiqPay
    const paymentStatus = searchParams.get('payment');
    if (paymentStatus === 'success') {
      showSuccess('Оплата успішно завершена!');
      setTimeout(() => {
        navigate('/orders');
      }, 2000);
    } else if (paymentStatus === 'failure') {
      showError('Помилка при оплаті. Спробуйте ще раз.');
    }
  }, [navigate, searchParams]);

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart/me');
      const cart = response.data;
      
      // Fetch menu item details for each cart item
      // Filter out items where menu item no longer exists
      const itemsWithDetails = await Promise.all(
        cart.items.map(async (item: CartItem) => {
          try {
            const menuResponse = await api.get(`/products/${item.menu_item_id}`);
            return {
              ...item,
              menu_item: menuResponse.data,
            };
          } catch (error: any) {
            // If menu item not found (404), skip this cart item
            if (error.response?.status === 404) {
              console.warn(`Menu item ${item.menu_item_id} not found, removing from cart`);
              // Optionally remove invalid cart item from backend
              try {
                await api.delete(`/cart/me/items/${item.id}`);
              } catch (deleteError) {
                console.error('Failed to remove invalid cart item:', deleteError);
              }
              return null;
            }
            throw error;
          }
        })
      );
      
      // Filter out null values (items with missing menu items)
      const validItems = itemsWithDetails.filter((item): item is CartItemWithDetails => item !== null);
      setCartItems(validItems);
    } catch (error) {
      console.error('Failed to fetch cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: number, newQuantity: number) => {
    if (newQuantity < 1) return;
    try {
      await api.put(`/cart/me/items/${itemId}`, { quantity: newQuantity });
      fetchCart();
      showSuccess('Кількість оновлено');
    } catch (error) {
      console.error('Failed to update quantity:', error);
      showError('Помилка оновлення кількості');
    }
  };

  const removeItem = async (itemId: number) => {
    // Додаємо анімацію видалення
    setRemovingItems((prev) => new Set(prev).add(itemId));
    
    setTimeout(async () => {
      try {
        await api.delete(`/cart/me/items/${itemId}`);
        await fetchCart();
        showSuccess('Товар видалено з кошика');
      } catch (error) {
        console.error('Failed to remove item:', error);
        showError('Помилка при видаленні');
        // Повертаємо стан назад при помилці
        setRemovingItems((prev) => {
          const next = new Set(prev);
          next.delete(itemId);
          return next;
        });
      }
    }, 300);
  };

  const clearCart = async () => {
    if (!confirm('Очистити весь кошик?')) return;
    try {
      await api.delete('/cart/me');
      setCartItems([]);
      showSuccess('Кошик очищено');
    } catch (error) {
      console.error('Failed to clear cart:', error);
      showError('Помилка очищення кошика');
    }
  };

  const getSubtotal = () => {
    return cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  const getDiscount = () => {
    return promoResult?.valid ? promoResult.discount : 0;
  };

  const getTotalPrice = () => {
    return getSubtotal() - getDiscount();
  };

  const validatePromo = async () => {
    if (!promoCode.trim()) return;
    setPromoLoading(true);
    try {
      const res = await api.post('/promo/validate', {
        code: promoCode.trim(),
        order_total: getSubtotal(),
      });
      setPromoResult(res.data);
      if (res.data.valid) {
        showSuccess('Промокод застосовано!');
      }
    } catch {
      setPromoResult({ valid: false, discount: 0, message: 'Помилка перевірки промокоду' });
    } finally {
      setPromoLoading(false);
    }
  };

  const clearPromo = () => {
    setPromoCode('');
    setPromoResult(null);
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) {
      showError('Будь ласка, введіть адресу доставки');
      return;
    }

    setProcessingOrder(true);

    try {
      const orderResponse = await api.post('/orders', {
        name: name.trim() || undefined,
        surname: surname.trim() || undefined,
        phone: phone.trim() || undefined,
        email: email.trim() || undefined,
        address,
        delivery_method: deliveryMethod,
        comment: comment.trim() || undefined,
        payment_method: 'card',
        promo_code: promoResult?.valid ? promoCode.trim() : undefined,
      });
      const orderId = orderResponse.data.id;

      // Отримуємо дані для LiqPay
      const paymentResponse = await api.post('/payments/create', null, {
        params: { order_id: orderId }
      });

      const { liqpay_data, liqpay_signature } = paymentResponse.data;

      // Показуємо форму оплати
      setPaymentData({
        data: liqpay_data,
        signature: liqpay_signature,
        orderId: orderId
      });
      setShowPayment(true);
      setProcessingOrder(false);
    } catch (error: any) {
      showError(error.response?.data?.detail || 'Помилка при створенні замовлення');
      setProcessingOrder(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-white"></div>
        </div>
      </div>
    );
  }

  if (showPayment && paymentData) {
    return (
      <div className="max-w-4xl mx-auto p-4 md:p-8">
        <LiqPayForm
          data={paymentData.data}
          signature={paymentData.signature}
          orderId={paymentData.orderId}
        />
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="text-center py-16 bg-white dark:bg-neutral-900 rounded-2xl border border-neutral-200 dark:border-neutral-700">
          <ShoppingCart className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-5" />
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-white mb-2">Ваш кошик порожній</h2>
          <p className="text-neutral-600 dark:text-neutral-400 mb-6 text-sm">Додайте товари з каталогу, щоб оформити замовлення.</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-neutral-900 dark:bg-white text-white dark:text-black px-6 py-3 rounded-full text-sm font-semibold hover:bg-black dark:hover:bg-neutral-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Переглянути меню
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl md:text-3xl font-semibold text-neutral-900 dark:text-white tracking-tight">Кошик</h1>
        <button
          onClick={clearCart}
          className="text-xs font-medium text-neutral-500 dark:text-neutral-400 hover:text-neutral-800 dark:hover:text-neutral-200 underline-offset-4 hover:underline"
        >
          Очистити все
        </button>
      </div>

      <form onSubmit={handleCheckout} className="space-y-6">
        {/* Cart Items */}
        <div className="space-y-3">
        {cartItems.map((item) => (
          <div
            key={item.id}
              className={`bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 transition-all duration-200 p-4 md:p-5 ${
              removingItems.has(item.id) ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
            }`}
          >
            <div className="flex gap-4">
              {item.menu_item.image_url ? (
                <img
                  src={item.menu_item.image_url}
                  alt={item.menu_item.name}
                  loading="lazy"
                    className="w-20 h-20 md:w-24 md:h-24 object-cover rounded-lg border border-neutral-200 dark:border-neutral-700"
                />
              ) : (
                  <div className="w-20 h-20 md:w-24 md:h-24 bg-neutral-100 dark:bg-neutral-800 rounded-lg flex items-center justify-center">
                    <span className="text-3xl text-neutral-300 dark:text-neutral-600">🛒</span>
                </div>
              )}

              <div className="flex-1 min-w-0">
                  <h3 className="text-sm md:text-base font-semibold text-neutral-900 dark:text-white mb-1 tracking-tight">
                  {item.menu_item.name}
                </h3>
                  {item.menu_item.description && (
                    <p className="text-xs text-neutral-600 dark:text-neutral-400 mb-1 line-clamp-2">
                  {item.menu_item.description}
                </p>
                  )}
                
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  {/* Кількість */}
                    <div className="flex items-center gap-1.5 bg-neutral-50 dark:bg-neutral-800 rounded-full px-1 py-0.5 border border-neutral-200 dark:border-neutral-700">
                    <button
                        type="button"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="p-2 rounded-lg hover:bg-white dark:hover:bg-neutral-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-90"
                      disabled={item.quantity <= 1}
                    >
                      <Minus className="w-4 h-4 text-neutral-700 dark:text-neutral-300" />
                    </button>
                      <span className="font-semibold text-sm w-8 text-center text-neutral-900 dark:text-white">
                      {item.quantity}
                    </span>
                    <button
                        type="button"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="p-2 rounded-lg hover:bg-white dark:hover:bg-neutral-700 transition-all active:scale-90"
                    >
                      <Plus className="w-4 h-4 text-neutral-700 dark:text-neutral-300" />
                    </button>
                  </div>

                  {/* Ціна та видалення */}
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                        <div className="text-xs text-neutral-500 dark:text-neutral-400">
                        ₴{(item.price / 100).toFixed(0)} × {item.quantity}
                      </div>
                        <div className="text-lg md:text-xl font-semibold text-neutral-900 dark:text-white">
                        ₴{((item.price * item.quantity) / 100).toFixed(0)}
                      </div>
                    </div>
                    <button
                        type="button"
                      onClick={() => removeItem(item.id)}
                        className="p-2 text-neutral-400 dark:text-neutral-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-full transition-all active:scale-90"
                      title="Видалити"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

        {/* Contact Info */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Контактні дані</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ім'я"
              className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
            />
            <input
              type="text"
              value={surname}
              onChange={(e) => setSurname(e.target.value)}
              placeholder="Прізвище"
              className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
            />
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="Телефон (+380...)"
              className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
            />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
            />
          </div>
        </div>

        {/* Delivery */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
              <Truck className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Доставка</h2>
          </div>
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2 mb-3">
              {[
                { value: 'nova_poshta', label: 'Нова Пошта' },
                { value: 'ukrposhta', label: 'Укрпошта' },
                { value: 'self_pickup', label: 'Самовивіз' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setDeliveryMethod(opt.value)}
                  className={`px-4 py-2.5 text-sm font-medium rounded-lg border transition-all duration-200 ${
                    deliveryMethod === opt.value
                      ? 'border-neutral-900 dark:border-white bg-neutral-900 dark:bg-white text-white dark:text-black'
                      : 'border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 hover:border-neutral-500 dark:hover:border-neutral-400'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-3 mb-2">
              <MapPin className="w-4 h-4 text-neutral-500 dark:text-neutral-400 flex-shrink-0" />
              <input
                type="text"
                required
                minLength={5}
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder={deliveryMethod === 'self_pickup' ? 'Адреса пункту самовивозу' : 'Адреса доставки (вул. Хрещатик, 1, кв. 5)'}
                className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
              />
            </div>
          </div>
        </div>

        {/* Comment */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Коментар до замовлення</h2>
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Ваші побажання до замовлення (необов'язково)"
            maxLength={1000}
            rows={3}
            className="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm resize-none bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
          />
        </div>

        {/* Promo Code */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center">
              <Tag className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">Промокод</h2>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={promoCode}
              onChange={(e) => { setPromoCode(e.target.value); if (promoResult) setPromoResult(null); }}
              placeholder="Введіть промокод"
              className="flex-1 px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-transparent text-sm uppercase bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
            />
            {promoResult?.valid ? (
              <button type="button" onClick={clearPromo} className="px-4 py-3 bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded-lg text-sm font-medium hover:bg-neutral-300 dark:hover:bg-neutral-600 transition-colors">
                <X className="w-4 h-4" />
              </button>
            ) : (
              <button
                type="button"
                onClick={validatePromo}
                disabled={promoLoading || !promoCode.trim()}
                className="px-5 py-3 bg-neutral-900 dark:bg-white text-white dark:text-black rounded-lg text-sm font-semibold hover:bg-black dark:hover:bg-neutral-200 transition-colors disabled:opacity-50"
              >
                {promoLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Перевірити'}
              </button>
            )}
          </div>
          {promoResult && (
            <div className={`mt-2 flex items-center gap-2 text-xs font-medium ${promoResult.valid ? 'text-green-600' : 'text-red-500'}`}>
              {promoResult.valid ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
              {promoResult.message}
              {promoResult.valid && <span className="ml-auto font-semibold">-₴{(promoResult.discount / 100).toFixed(2)}</span>}
            </div>
          )}
        </div>

        {/* Order Summary */}
        <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5">
          <h3 className="text-base font-semibold text-neutral-900 dark:text-white mb-3">Підсумок замовлення</h3>

          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-xs text-neutral-600 dark:text-neutral-400">
              <span>Товари ({cartItems.length} шт)</span>
              <span className="font-medium">₴{(getSubtotal() / 100).toFixed(2)}</span>
            </div>
            {getDiscount() > 0 && (
              <div className="flex justify-between text-xs text-green-600 font-medium">
                <span>Знижка (промокод)</span>
                <span>-₴{(getDiscount() / 100).toFixed(2)}</span>
              </div>
            )}
            <div className="border-t border-neutral-200 dark:border-neutral-700 pt-3 flex justify-between items-center mt-2">
              <span className="text-sm font-medium text-neutral-600 dark:text-neutral-400">Разом до сплати</span>
              <span className="text-2xl font-semibold text-neutral-900 dark:text-white">
              ₴{(getTotalPrice() / 100).toFixed(2)}
            </span>
          </div>
        </div>

          <button
            type="submit"
            disabled={processingOrder || getTotalPrice() === 0}
            className="w-full bg-neutral-900 dark:bg-white text-white dark:text-black py-3 px-6 rounded-full text-sm font-semibold hover:bg-black dark:hover:bg-neutral-200 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processingOrder ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Створення замовлення...
              </>
            ) : (
              <>
            Оформити замовлення
            <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
          
          <Link
            to="/"
            className="w-full mt-2 flex items-center justify-center gap-2 bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 py-2.5 px-6 rounded-full text-sm font-medium hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Продовжити покупки
          </Link>
        </div>
      </form>
    </div>
  );
}
