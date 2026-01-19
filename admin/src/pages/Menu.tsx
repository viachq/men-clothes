import { useEffect, useState } from 'react';
import api from '../api/client';
import type { MenuItem, Category } from '../types';
import { Plus, Edit, Trash2, Shirt, FolderOpen } from 'lucide-react';
import Card from '../components/ui/Card';


type TabType = 'items' | 'categories';

export default function Menu() {
  const [activeTab, setActiveTab] = useState<TabType>('items');
  
  // Items state
  const [items, setItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<MenuItem | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', price: 0, category_id: null as number | null, image_url: '' });
  const [categoryFilter, setCategoryFilter] = useState<number | null>(null);
  
  // Categories state
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);
  const [categoryModalOpen, setCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  const [categoryFormData, setCategoryFormData] = useState({ name: '' });

  useEffect(() => {
    fetchItems();
    fetchCategories();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await api.get('/products/');
      setItems(response.data);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories/');
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    } finally {
      setCategoriesLoading(false);
    }
  };


  // Items handlers
  const handleItemSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingItem) {
        await api.put(`/admin/products/${editingItem.id}`, formData);
      } else {
        await api.post('/admin/products', formData);
      }
      fetchItems();
      setModalOpen(false);
      setFormData({ name: '', description: '', price: 0, category_id: null, image_url: '' });
      setEditingItem(null);
    } catch (error) {
      console.error('Failed to save item:', error);
    }
  };

  const handleItemDelete = async (id: number) => {
    if (!confirm('Видалити цей товар?')) return;
    try {
      await api.delete(`/admin/products/${id}`);
      fetchItems();
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const openItemModal = (item?: MenuItem) => {
    if (item) {
      setEditingItem(item);
      setFormData({ 
        name: item.name, 
        description: item.description || '', 
        price: item.price, 
        category_id: item.category_id,
        image_url: item.image_url || ''
      });
    } else {
      setEditingItem(null);
      setFormData({ name: '', description: '', price: 0, category_id: null, image_url: '' });
    }
    setModalOpen(true);
  };

  // Categories handlers
  const handleCategorySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingCategory) {
        await api.put(`/admin/categories/${editingCategory.id}`, categoryFormData);
      } else {
        await api.post('/admin/categories', categoryFormData);
      }
      fetchCategories();
      setCategoryModalOpen(false);
      setCategoryFormData({ name: '' });
      setEditingCategory(null);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Не вдалося зберегти категорію');
    }
  };

  const handleCategoryDelete = async (id: number) => {
    if (!confirm('Видалити цю категорію? Всі товари стануть без категорії.')) return;
    try {
      await api.delete(`/admin/categories/${id}`);
      fetchCategories();
    } catch (error) {
      console.error('Failed to delete category:', error);
    }
  };

  const openCategoryModal = (category?: Category) => {
    if (category) {
      setEditingCategory(category);
      setCategoryFormData({ name: category.name });
    } else {
      setEditingCategory(null);
      setCategoryFormData({ name: '' });
    }
    setCategoryModalOpen(true);
  };

  if (loading || categoriesLoading) {
    return <div className="flex justify-center p-8"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div></div>;
  }

  const filteredItems = categoryFilter
    ? items.filter((item) => item.category_id === categoryFilter)
    : items;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with tabs */}
      <div className="mb-6">
        {/* Tabs */}
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between border-b border-neutral-200 mb-4">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('items')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'items'
                  ? 'text-neutral-900 border-b-2 border-neutral-900'
                  : 'text-neutral-500 hover:text-neutral-700'
              }`}
            >
              Товари
            </button>
            <button
              onClick={() => setActiveTab('categories')}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === 'categories'
                  ? 'text-neutral-900 border-b-2 border-neutral-900'
                  : 'text-neutral-500 hover:text-neutral-700'
              }`}
            >
              Категорії
            </button>
          </div>

          {/* Right side controls */}
          {activeTab === 'categories' && (
            <button 
              onClick={() => openCategoryModal()} 
              className="inline-flex items-center gap-2 bg-neutral-900 text-white px-5 py-2.5 rounded-lg hover:bg-neutral-800 transition-colors font-medium text-sm"
            >
              <Plus className="w-4 h-4" /> Додати категорію
            </button>
          )}

          {activeTab === 'items' && (
            <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto sm:items-center justify-end">
              <select
                value={categoryFilter || ''}
                onChange={(e) =>
                  setCategoryFilter(e.target.value ? Number(e.target.value) : null)
                }
                className="w-full sm:w-56 px-3 py-2 border border-neutral-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
              >
                <option value="">Всі категорії ({items.length})</option>
                {categories.map((category) => {
                  const count = items.filter(
                    (item) => item.category_id === category.id
                  ).length;
                  return (
                    <option key={category.id} value={category.id}>
                      {category.name} ({count})
                    </option>
                  );
                })}
              </select>

              <button 
                onClick={() => openItemModal()} 
                className="inline-flex items-center justify-center gap-2 bg-neutral-900 text-white px-5 py-2.5 rounded-lg hover:bg-neutral-800 transition-colors font-medium text-sm whitespace-nowrap"
              >
                <Plus className="w-4 h-4" /> Додати товар
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Items Tab */}
      {activeTab === 'items' && (
        <>
          {/* Items Grid */}
          {filteredItems.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border border-neutral-200">
              <p className="text-neutral-500 text-lg">Товари не знайдені</p>
              <p className="text-neutral-400 text-sm mt-2">Спробуйте змінити фільтр або додати нові товари</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-5 md:gap-6 lg:gap-8">
              {filteredItems.map((item) => {
                // Stats removed - endpoint no longer available
                
                return (
                  <Card
                    key={item.id}
                    padding="none"
                    className="overflow-hidden border border-neutral-200 rounded-sm bg-white group hover:shadow-xl transition-all duration-500"
                  >
                    {/* Image Container - matching client side with aspect-square */}
                    <div className="relative overflow-hidden aspect-square bg-white">
                      {item.image_url ? (
                        <img 
                          src={item.image_url} 
                          alt={item.name} 
                          className="w-full h-full object-cover transition-transform duration-[800ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-115" 
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-neutral-50 to-neutral-100 flex items-center justify-center">
                          <span className="text-6xl text-neutral-200">👕</span>
                        </div>
                      )}

                      {/* Top gradient bar */}
                      <div className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-neutral-900 via-neutral-700 to-neutral-900" />

                      {/* Price pill */}
                      <div className="absolute bottom-3 right-3">
                        <div className="px-3 py-1 rounded-full bg-black/80 text-white text-xs font-semibold shadow-lg">
                          ₴{(item.price / 100).toFixed(0)}
                        </div>
                      </div>
                    </div>

                    {/* Content - matching client side structure */}
                    <div className="flex flex-col flex-1 px-1 py-4">
                      <h3 className="text-sm md:text-base font-semibold text-black mb-2 tracking-tight leading-snug line-clamp-2">
                        {item.name}
                      </h3>
                      
                      {/* Description */}
                      {item.description && (
                        <p className="text-xs text-neutral-500 mb-2 line-clamp-2 leading-relaxed">
                          {item.description}
                        </p>
                      )}
                      
                      {/* Actions */}
                      <div className="flex items-center justify-between mt-auto pt-2 border-t border-neutral-100">
                        <span className="text-[9px] text-neutral-400">ID: {item.id}</span>
                        <div className="flex gap-1.5">
                          <button
                            onClick={() => openItemModal(item)}
                            className="w-7 h-7 rounded-full bg-neutral-100 hover:bg-neutral-900 hover:text-white flex items-center justify-center transition-colors"
                            aria-label="Редагувати товар"
                          >
                            <Edit className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleItemDelete(item.id)}
                            className="w-7 h-7 rounded-full bg-neutral-100 hover:bg-red-500 hover:text-white flex items-center justify-center transition-colors"
                            aria-label="Видалити товар"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Categories Tab */}
      {activeTab === 'categories' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {categories.map((category) => {
            return (
              <div 
                key={category.id} 
                className="relative bg-white border-2 border-neutral-200 rounded-2xl overflow-hidden hover:border-neutral-400 hover:shadow-2xl transition-all duration-300 group"
              >
                {/* Top accent bar */}
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-neutral-900 via-neutral-700 to-neutral-900"></div>
                
                <div className="p-6">
                  {/* Icon with background pattern */}
                  <div className="relative mb-5">
                    <div className="absolute inset-0 bg-neutral-100 rounded-xl opacity-50 group-hover:opacity-70 transition-opacity"></div>
                    <div className="relative w-20 h-20 mx-auto bg-gradient-to-br from-neutral-900 to-neutral-700 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                      <Shirt className="w-10 h-10 text-white" strokeWidth={2} />
                    </div>
                  </div>
                  
                  {/* Category name */}
                  <h3 className="text-lg font-black text-neutral-900 mb-3 text-center tracking-tight uppercase">
                    {category.name}
                  </h3>
                  
                  {/* Product count */}
                  
                  {/* Action buttons */}
                  <div className="flex gap-2 pt-4 border-t border-neutral-100">
                    <button
                      onClick={() => openCategoryModal(category)}
                      className="flex-1 py-2.5 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-50 rounded-lg transition-colors font-medium text-sm"
                      aria-label="Редагувати категорію"
                    >
                      <Edit className="w-4 h-4 mx-auto" />
                    </button>
                    <div className="w-px bg-neutral-200"></div>
                    <button
                      onClick={() => handleCategoryDelete(category.id)}
                      className="flex-1 py-2.5 text-neutral-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium text-sm"
                      aria-label="Видалити категорію"
                    >
                      <Trash2 className="w-4 h-4 mx-auto" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {categories.length === 0 && activeTab === 'categories' && (
        <div className="text-center py-12 bg-white rounded-xl">
          <FolderOpen className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <p className="text-neutral-500">Поки що немає категорій. Додайте першу категорію!</p>
        </div>
      )}

      {/* Item Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 py-8">
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
            <div className="relative bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border-2 border-neutral-200 max-h-[90vh] overflow-y-auto">
              {/* Header with gradient accent */}
              <div className="relative bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 px-8 py-6 sticky top-0 z-10">
                <div className="absolute top-0 left-0 right-0 h-1 bg-white/20"></div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                    <Shirt className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-black text-white tracking-tight uppercase">
                    {editingItem ? 'Редагувати товар' : 'Новий товар'}
                  </h2>
                </div>
                <p className="text-white/70 text-sm">Заповніть інформацію про товар</p>
              </div>
              
              <form onSubmit={handleItemSubmit} className="p-8 space-y-5">
                <div>
                  <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                    Назва товару
                  </label>
                  <input 
                    type="text" 
                    required 
                    value={formData.name} 
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })} 
                    className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400" 
                    placeholder="Введіть назву товару"
                  />
                </div>
                
                <div>
                  <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                    Опис
                  </label>
                  <textarea 
                    value={formData.description} 
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })} 
                    className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400 resize-none" 
                    rows={4}
                    placeholder="Додайте опис товару..."
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                      Категорія
                    </label>
                    <select 
                      value={formData.category_id || ''} 
                      onChange={(e) => setFormData({ ...formData, category_id: e.target.value ? Number(e.target.value) : null })} 
                      className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900"
                    >
                      <option value="">Без категорії</option>
                      {categories.map(cat => (
                        <option key={cat.id} value={cat.id}>{cat.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                      Ціна (в копійках)
                    </label>
                    <input 
                      type="number" 
                      required 
                      value={formData.price} 
                      onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })} 
                      className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400" 
                      placeholder="0"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                    URL зображення
                  </label>
                  <input 
                    type="text" 
                    value={formData.image_url} 
                    onChange={(e) => setFormData({ ...formData, image_url: e.target.value })} 
                    className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400 font-mono text-sm" 
                    placeholder="https://example.com/image.jpg"
                  />
                </div>
                
                <div className="flex gap-3 pt-4 border-t border-neutral-100">
                  <button
                    type="button"
                    onClick={() => setModalOpen(false)}
                    className="flex-1 py-3.5 bg-neutral-100 text-neutral-700 rounded-xl hover:bg-neutral-200 transition-colors font-semibold text-sm"
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

      {/* Category Modal */}
      {categoryModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4">
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setCategoryModalOpen(false)} />
            <div className="relative bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border-2 border-neutral-200">
              {/* Header with gradient accent */}
              <div className="relative bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 px-8 py-6">
                <div className="absolute top-0 left-0 right-0 h-1 bg-white/20"></div>
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center">
                    <Shirt className="w-5 h-5 text-white" />
                  </div>
                  <h2 className="text-2xl font-black text-white tracking-tight uppercase">
                    {editingCategory ? 'Редагувати категорію' : 'Нова категорія'}
                  </h2>
                </div>
                <p className="text-white/70 text-sm">Введіть назву категорії для одягу</p>
              </div>
              
              <form onSubmit={handleCategorySubmit} className="p-8">
                <div className="mb-6">
                  <label className="block text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">
                    Назва категорії
                  </label>
                  <div className="relative">
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400">
                      <Shirt className="w-5 h-5" />
                    </div>
                    <input
                      type="text"
                      required
                      value={categoryFormData.name}
                      onChange={(e) => setCategoryFormData({ name: e.target.value })}
                      className="w-full pl-12 pr-4 py-4 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400"
                      placeholder="Наприклад: Polo Shirts, Sweaters..."
                    />
                  </div>
                  <p className="mt-2 text-xs text-neutral-500">Введіть унікальну назву для нової категорії товарів</p>
                </div>
                
                <div className="flex gap-3 pt-4 border-t border-neutral-100">
                  <button
                    type="button"
                    onClick={() => setCategoryModalOpen(false)}
                    className="flex-1 py-3.5 bg-neutral-100 text-neutral-700 rounded-xl hover:bg-neutral-200 transition-colors font-semibold text-sm"
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
