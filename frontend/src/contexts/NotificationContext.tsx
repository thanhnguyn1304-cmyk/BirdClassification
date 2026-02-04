import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import axios from 'axios';

interface Notification {
    id: string;
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
}

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    markAllAsRead: () => void;
    removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export function NotificationProvider({ children }: { children: ReactNode }) {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [lastTotal, setLastTotal] = useState<number | null>(null);

    // Poll for new detections
    useEffect(() => {
        const checkNewDetections = async () => {
            try {
                // We use the summary endpoint as a lightweight check
                const res = await axios.get('/api/analytics/summary');
                const currentTotal = res.data.total_detections;
                const recentSpecies = res.data.most_recent?.species;

                if (lastTotal !== null && currentTotal > lastTotal) {
                    // New detection found!
                    const countDiff = currentTotal - lastTotal;

                    const newNotif: Notification = {
                        id: Date.now().toString(),
                        title: 'New Bird Detected! 🐦',
                        message: countDiff === 1
                            ? `A wild ${recentSpecies || 'Bird'} just appeared!`
                            : `${countDiff} new birds detected!`,
                        timestamp: new Date(),
                        read: false
                    };

                    setNotifications(prev => [newNotif, ...prev]);

                    // Audio alert (optional, subtle beep)
                    // const audio = new Audio('/notification.mp3');
                    // audio.play().catch(() => {}); 
                }

                setLastTotal(currentTotal);
            } catch (error) {
                console.error("Polling error:", error);
            }
        };

        // Initial check
        checkNewDetections();

        // Poll every 5 seconds
        const interval = setInterval(checkNewDetections, 5000);
        return () => clearInterval(interval);
    }, [lastTotal]);

    const unreadCount = notifications.filter(n => !n.read).length;

    const markAllAsRead = () => {
        setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    };

    const removeNotification = (id: string) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    return (
        <NotificationContext.Provider value={{ notifications, unreadCount, markAllAsRead, removeNotification }}>
            {children}
        </NotificationContext.Provider>
    );
}

export function useNotifications() {
    const context = useContext(NotificationContext);
    if (context === undefined) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
}
