export interface User {
  id: number;
  username: string;
  role: 'client' | 'manager' | 'system_admin';
}

export interface Order {
  id: number;
  user_id: number;
  status: string;
  total_price: number;
  delivery_address: string;
  delivery_time: string | null;
  created_at: string;
  payment_method: string;
}

export interface OrderDetails extends Order {
  updated_at: string;
  items: OrderItem[];
}

export interface OrderItem {
  id: number;
  menu_item_id: number;
  menu_item_name: string;
  quantity: number;
  price: number;
  subtotal: number;
}

export interface MenuItem {
  id: number;
  name: string;
  description: string | null;
  price: number;
  category_id: number | null;
  image_url: string | null;
}

export interface Category {
  id: number;
  name: string;
  description: string | null;
}

export interface Store {
  id: number;
  name: string;
  description: string;
  address: string;
  phone: string;
  opening_hours: string;
}

