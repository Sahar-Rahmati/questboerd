function urlBase64ToUint8Array(base64String) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

export function isPushSupported() {
  return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
}

export async function registerPushServiceWorker() {
  if (!isPushSupported()) {
    return null;
  }
  return navigator.serviceWorker.register("/sw.js");
}

export async function subscribeToPush(vapidPublicKey) {
  const registration = await registerPushServiceWorker();
  if (!registration) {
    throw new Error("This browser does not support push notifications.");
  }

  const existing = await registration.pushManager.getSubscription();
  if (existing) {
    return existing;
  }

  return registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
  });
}

export async function getCurrentSubscription() {
  if (!isPushSupported()) {
    return null;
  }
  const registration = await navigator.serviceWorker.ready;
  return registration.pushManager.getSubscription();
}

export async function unsubscribeFromPush() {
  const subscription = await getCurrentSubscription();
  if (subscription) {
    await subscription.unsubscribe();
  }
  return subscription;
}

export async function showLocalNotificationPreview({ title, body }) {
  if (!isPushSupported()) {
    throw new Error("This browser does not support notifications.");
  }

  const registration = await navigator.serviceWorker.ready;
  await registration.showNotification(title, {
    body,
    tag: "questboard-reminder-preview",
  });
}
