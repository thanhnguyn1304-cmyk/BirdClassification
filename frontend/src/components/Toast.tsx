import { useEffect } from 'react';
import { X, Bird } from 'lucide-react';
import { useNotifications } from '../contexts/NotificationContext';

export function ToastContainer() {
    const { notifications, removeNotification } = useNotifications();

    // Only show unread notifications in the toaster
    const activeToasts = notifications.filter(n => !n.read).slice(0, 3); // Max 3 at a time

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-4">
            {activeToasts.map((notif) => (
                <Toast
                    key={notif.id}
                    id={notif.id}
                    title={notif.title}
                    message={notif.message}
                    onClose={() => removeNotification(notif.id)}
                />
            ))}
        </div>
    );
}

function Toast({ id, title, message, onClose }: { id: string, title: string, message: string, onClose: () => void }) {

    // Auto-dismiss after 5 seconds
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 5000);
        return () => clearTimeout(timer);
    }, [id, onClose]);

    return (
        <div className="bg-white border-3 border-ink-black rounded-xl shadow-brutal-lg p-4 w-80 transform transition-all animate-in slide-in-from-right duration-300 flex gap-3 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-2 h-full bg-sun-yellow"></div>

            <div className="p-2 bg-sand-light rounded-lg h-fit">
                <Bird className="w-6 h-6 text-ink-black" />
            </div>

            <div className="flex-1">
                <h4 className="font-display font-bold text-ink-black">{title}</h4>
                <p className="text-sm text-ink-gray font-body">{message}</p>
            </div>

            <button
                onClick={onClose}
                className="text-ink-gray hover:text-ink-black transition-colors"
            >
                <X className="w-5 h-5" />
            </button>
        </div>
    );
}
