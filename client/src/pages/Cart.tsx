import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import type { CartItem, MenuItem } from '../types';
import { ShoppingCart, Trash2, Plus, Minus, ArrowRight } from 'lucide-react';

interface CartItemWithDetails extends CartItem {
  menu_item: MenuItem;
}

export default function Cart() {
  const [cartItems, setCartItems] = useState<CartItemWithDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('client_token')) {
      navigate('/login');
      return;
    }
    fetchCart();
  }, [navigate]);

  const fetchCart = async () => {
    try {
      const response = await api.get('/cart/me');
      const cart = response.data;
      
      // Fetch menu item details for each cart item
      const itemsWithDetails = await Promise.all(
        cart.items.map(async (item: CartItem) => {
          const menuResponse = await api.get(`/menu/${item.menu_item_id}`);
          return {
            ...item,
            menu_item: menuResponse.data,
          };
        })
      );
      
      setCartItems(itemsWithDetails);
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
    } catch (error) {
      console.error('Failed to update quantity:', error);
    }
  };

  const removeItem = async (itemId: number) => {
    try {
      await api.delete(`/cart/me/items/${itemId}`);
      fetchCart();
    } catch (error) {
      console.error('Failed to remove item:', error);
    }
  };

  const clearCart = async () => {
    if (!confirm('Очистити весь кошик?')) return;
    try {
      await api.delete('/cart/me');
      setCartItems([]);
    } catch (error) {
      console.error('Failed to clear cart:', error);
    }
  };

  const getTotalPrice = () => {
    return cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
        </div>
      </div>
    );
  }

  if (cartItems.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <div className="text-center py-16 bg-white rounded-xl">
          <ShoppingCart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ваш кошик порожній</h2>
          <p className="text-gray-600 mb-6">Додайте страви з меню</p>
          <a
            href="/"
            className="inline-block bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700"
          >
            Переглянути меню
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Кошик</h1>
        <button
          onClick={clearCart}
          className="text-red-600 hover:text-red-700 font-medium text-sm"
        >
          Очистити все
        </button>
      </div>

      <div className="space-y-4 mb-8">
        {cartItems.map((item) => (
          <div key={item.id} className="bg-white rounded-xl shadow-sm p-4 md:p-6">
            <div className="flex gap-4">
              {item.menu_item.image_url ? (
                <img
                  src={item.menu_item.image_url}
                  alt={item.menu_item.name}
                  className="w-24 h-24 object-cover rounded-lg"
                />
              ) : (
                <div className="w-24 h-24 bg-gradient-to-br from-red-400 to-orange-400 rounded-lg flex items-center justify-center">
                  <span className="text-3xl">🍕</span>
                </div>
              )}

              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-1">
                  {item.menu_item.name}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  {item.menu_item.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="p-1 rounded-lg hover:bg-gray-100"
                      disabled={item.quantity <= 1}
                    >
                      <Minus className="w-5 h-5 text-gray-600" />
                    </button>
                    <span className="font-medium text-lg w-8 text-center">
                      {item.quantity}
                    </span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="p-1 rounded-lg hover:bg-gray-100"
                    >
                      <Plus className="w-5 h-5 text-gray-600" />
                    </button>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="text-xl font-bold text-red-600">
                      ₴{((item.price * item.quantity) / 100).toFixed(2)}
                    </span>
                    <button
                      onClick={() => removeItem(item.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
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

      {/* Total and Checkout */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-6 pb-6 border-b">
          <span className="text-xl font-medium text-gray-900">Разом:</span>
          <span className="text-3xl font-bold text-red-600">
            ₴{(getTotalPrice() / 100).toFixed(2)}
          </span>
        </div>
        <button
          onClick={() => navigate('/checkout')}
          className="w-full bg-red-600 text-white py-4 px-6 rounded-lg font-medium hover:bg-red-700 flex items-center justify-center gap-2"
        >
          Оформити замовлення
          <ArrowRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

