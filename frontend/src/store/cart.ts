import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Product = { id: number; name: string; price: number, img?: string };
export type CartItem = Product & { qty: number };

type CartState = {
    items: CartItem[]
    coupon?: string
    add: (p: Product, qty?: number) => void
    remove: (id: number) => void
    setQty: (id: number, qty: number) => void
    setCoupon: (code?: string) => void
    clear: () => void
    subtotal: () => number
    total: () => number
}

export const useCart = create<CartState>()(
    persist(
        (set, get) => ({
            items: [],
            coupon: undefined,
            add: (p, qty = 1) =>
                set(state => {
                    const items = [...state.items];
                    const idx = items.findIndex(i => i.id === p.id);
                    if (idx >= 0) items[idx] = { ...items[idx], qty: items[idx].qty + qty };
                    else items.push({ ...p, qty });
                    return { items };
                }),
            remove: (id) => set(state => ({ items: state.items.filter(i => i.id !== id) })),
            setQty: (id, qty) =>
                set(state => {
                    const items = state.items.map(i => i.id === id ? { ...i, qty: Math.max(1, qty) } : i);
                    return { items };
                }),
            setCoupon: (code) => set({ coupon: code?.trim() || undefined }),
            clear: () => set({ items: [], coupon: undefined }),
            subtotal: () => get().items.reduce((a, i) => a + i.price * i.qty, 0),
            total: () => {
                const sub = get().subtotal();
                return get().coupon === 'HOLA10' ? Math.round(sub * 0.9) : sub;
            }
        }),
        {name: 'cart-store'}
    )
)