import { useEffect, useState, useRef } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import api from '../api/client';
import type { CartItem, MenuItem } from '../types';
import { ShoppingCart, Trash2, Plus, Minus, ArrowRight, ArrowLeft, MapPin, Loader2 } from 'lucide-react';
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
      <div className="rounded-xl border border-neutral-200 bg-white p-6">
        <div className="mb-4 flex items-center justify-between text-base">
          <span className="text-neutral-600">Замовлення #{orderId}</span>
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
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-900 mx-auto" />
          <p className="text-sm text-neutral-600">Перенаправлення на сторінку оплати LiqPay...</p>
        </div>
      </div>
    </div>
  );
}

export default function Cart() {
  const [cartItems, setCartItems] = useState<CartItemWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [removingItems, setRemovingItems] = useState<Set<number>>(new Set());
  const [address, setAddress] = useState('');
  const [processingOrder, setProcessingOrder] = useState(false);
  const [showPayment, setShowPayment] = useState(false);
  const [paymentData, setPaymentData] = useState<{ data: string; signature: string; orderId: number } | null>(null);
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

  const getTotalPrice = () => {
    return cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  const handleCheckout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) {
      showError('Будь ласка, введіть адресу доставки');
      return;
    }

    setProcessingOrder(true);

    try {
      // Створюємо замовлення
      const orderResponse = await api.post('/orders', { address });
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
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
        <div className="text-center py-16 bg-white rounded-2xl border border-neutral-200">
          <ShoppingCart className="w-16 h-16 text-neutral-300 mx-auto mb-5" />
          <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Ваш кошик порожній</h2>
          <p className="text-neutral-600 mb-6 text-sm">Додайте товари з каталогу, щоб оформити замовлення.</p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 bg-neutral-900 text-white px-6 py-3 rounded-full text-sm font-semibold hover:bg-black transition-colors"
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
        <h1 className="text-2xl md:text-3xl font-semibold text-neutral-900 tracking-tight">Кошик</h1>
        <button
          onClick={clearCart}
          className="text-xs font-medium text-neutral-500 hover:text-neutral-800 underline-offset-4 hover:underline"
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
              className={`bg-white rounded-xl border border-neutral-200 transition-all duration-200 p-4 md:p-5 ${
              removingItems.has(item.id) ? 'opacity-0 scale-95' : 'opacity-100 scale-100'
            }`}
          >
            <div className="flex gap-4">
              {item.menu_item.image_url ? (
                <img
                  src={item.menu_item.image_url}
                  alt={item.menu_item.name}
                  loading="lazy"
                    className="w-20 h-20 md:w-24 md:h-24 object-cover rounded-lg border border-neutral-200"
                />
              ) : (
                  <div className="w-20 h-20 md:w-24 md:h-24 bg-neutral-100 rounded-lg flex items-center justify-center">
                    <span className="text-3xl text-neutral-300">🛒</span>
                </div>
              )}

              <div className="flex-1 min-w-0">
                  <h3 className="text-sm md:text-base font-semibold text-neutral-900 mb-1 tracking-tight">
                  {item.menu_item.name}
                </h3>
                  {item.menu_item.description && (
                    <p className="text-xs text-neutral-600 mb-1 line-clamp-2">
                  {item.menu_item.description}
                </p>
                  )}
                
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  {/* Кількість */}
                    <div className="flex items-center gap-1.5 bg-neutral-50 rounded-full px-1 py-0.5 border border-neutral-200">
                    <button
                        type="button"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="p-2 rounded-lg hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-90"
                      disabled={item.quantity <= 1}
                    >
                      <Minus className="w-4 h-4 text-neutral-700" />
                    </button>
                      <span className="font-semibold text-sm w-8 text-center text-neutral-900">
                      {item.quantity}
                    </span>
                    <button
                        type="button"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="p-2 rounded-lg hover:bg-white transition-all active:scale-90"
                    >
                      <Plus className="w-4 h-4 text-neutral-700" />
                    </button>
                  </div>

                  {/* Ціна та видалення */}
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                        <div className="text-xs text-neutral-500">
                        ₴{(item.price / 100).toFixed(0)} × {item.quantity}
                      </div>
                        <div className="text-lg md:text-xl font-semibold text-neutral-900">
                        ₴{((item.price * item.quantity) / 100).toFixed(0)}
                      </div>
                    </div>
                    <button
                        type="button"
                      onClick={() => removeItem(item.id)}
                        className="p-2 text-neutral-400 hover:text-red-600 hover:bg-red-50 rounded-full transition-all active:scale-90"
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

        {/* Delivery Address */}
        <div className="bg-white rounded-xl border border-neutral-200 p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 flex items-center justify-center">
              <MapPin className="w-5 h-5 text-neutral-700" />
            </div>
            <h2 className="text-lg font-semibold text-neutral-900">Адреса доставки</h2>
          </div>
          <input
            type="text"
            required
            minLength={5}
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            placeholder="наприклад: вул. Хрещатик, 1, кв. 5"
            className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-neutral-900 focus:border-transparent text-sm"
          />
          <p className="mt-2 text-xs text-neutral-500">
            Введіть повну адресу з вулицею, будинком та квартирою
          </p>
        </div>

        {/* Order Summary */}
        <div className="bg-white rounded-xl border border-neutral-200 p-5">
          <h3 className="text-base font-semibold text-neutral-900 mb-3">Підсумок замовлення</h3>
          
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-xs text-neutral-600">
              <span>Товари ({cartItems.length} шт)</span>
              <span className="font-medium">₴{(getTotalPrice() / 100).toFixed(2)}</span>
          </div>
            <div className="border-t border-neutral-200 pt-3 flex justify-between items-center mt-2">
              <span className="text-sm font-medium text-neutral-600">Разом до сплати</span>
              <span className="text-2xl font-semibold text-neutral-900">
              ₴{(getTotalPrice() / 100).toFixed(2)}
            </span>
          </div>
        </div>

          <button
            type="submit"
            disabled={processingOrder || getTotalPrice() === 0}
            className="w-full bg-neutral-900 text-white py-3 px-6 rounded-full text-sm font-semibold hover:bg-black transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
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
            className="w-full mt-2 flex items-center justify-center gap-2 bg-neutral-100 text-neutral-700 py-2.5 px-6 rounded-full text-sm font-medium hover:bg-neutral-200 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Продовжити покупки
          </Link>
        </div>
      </form>
    </div>
  );
}
