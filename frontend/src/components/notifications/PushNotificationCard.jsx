import { useEffect, useState } from "react";
import client from "../../api/client";
import {
  getCurrentSubscription,
  isPushSupported,
  registerPushServiceWorker,
  showLocalNotificationPreview,
  subscribeToPush,
  unsubscribeFromPush,
} from "../../services/pushNotifications";

function getPermissionLabel() {
  if (!isPushSupported()) {
    return "unsupported";
  }
  return Notification.permission;
}

export default function PushNotificationCard() {
  const [config, setConfig] = useState(null);
  const [permission, setPermission] = useState(getPermissionLabel());
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const refreshConfig = async () => {
    const response = await client.get("/notifications/push-config/");
    setConfig(response.data);
    setPermission(getPermissionLabel());
  };

  useEffect(() => {
    if (isPushSupported()) {
      registerPushServiceWorker().catch(() => {
        // Ignore background registration issues here and surface action errors only.
      });
    }

    refreshConfig()
      .catch(() => setError("Unable to load reminder settings."))
      .finally(() => setLoading(false));
  }, []);

  const handleEnable = async () => {
    setActionLoading(true);
    setError("");
    setMessage("");
    try {
      if (!isPushSupported()) {
        throw new Error("This browser does not support web push notifications.");
      }
      if (!config?.is_configured) {
        throw new Error("Push keys are not configured on the server yet.");
      }

      const granted = await Notification.requestPermission();
      setPermission(granted);
      if (granted !== "granted") {
        throw new Error("Notification permission was not granted.");
      }

      await showLocalNotificationPreview({
        title: "Reminders are on",
        body: "You will get a reminder when your scheduled task is due.",
      });

      const subscription = await subscribeToPush(config.vapid_public_key);
      const serialized = subscription.toJSON();
      await client.post("/notifications/subscriptions/", {
        endpoint: serialized.endpoint,
        expiration_time: serialized.expirationTime ?? null,
        keys: serialized.keys,
      });
      await refreshConfig();
      setMessage("Task reminders are enabled for this browser.");
    } catch (enableError) {
      setError(enableError.response?.data?.detail || enableError.message || "Unable to enable reminders.");
    } finally {
      setActionLoading(false);
    }
  };

  const handlePrepareBrowserNotifications = async () => {
    setActionLoading(true);
    setError("");
    setMessage("");
    try {
      if (!isPushSupported()) {
        throw new Error("This browser does not support web push notifications.");
      }
      const granted = await Notification.requestPermission();
      setPermission(granted);
      if (granted !== "granted") {
        throw new Error("Notification permission was not granted.");
      }
      await showLocalNotificationPreview({
        title: "Notifications are allowed",
        body: "This device is ready to receive reminders.",
      });
      setMessage("This device is ready to receive reminders.");
    } catch (prepareError) {
      setError(prepareError.message || "Unable to prepare browser notifications.");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisable = async () => {
    setActionLoading(true);
    setError("");
    setMessage("");
    try {
      const subscription = await getCurrentSubscription();
      if (subscription) {
        await client.post("/notifications/subscriptions/deactivate/", { endpoint: subscription.endpoint });
        await unsubscribeFromPush();
      }
      await refreshConfig();
      setMessage("Task reminders were disabled for this browser.");
    } catch (disableError) {
      setError(disableError.response?.data?.detail || disableError.message || "Unable to disable reminders.");
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="panel p-5">
        <p className="text-sm text-slate-500">Loading reminder settings...</p>
      </div>
    );
  }

  const isEnabled = Boolean(config?.has_active_subscription);
  const serverReady = Boolean(config?.is_configured);

  return (
    <div className="panel p-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-ember">Web Push Reminders</p>
          <h3 className="mt-2 text-2xl font-bold text-brand-ink">Task reminders</h3>
          <p className="mt-2 text-sm text-slate-600">
            Turn on reminders to stay on schedule and catch your next task on time.
          </p>
        </div>
        <div className={`rounded-2xl px-4 py-3 text-right ${isEnabled ? "bg-brand-mint/60" : "bg-slate-100"}`}>
          <p className="text-xs uppercase tracking-[0.15em] text-slate-500">Status</p>
          <p className="mt-1 text-lg font-semibold text-brand-ink">{isEnabled ? "Enabled" : "Disabled"}</p>
          <p className="text-xs text-slate-500">Browser permission: {permission}</p>
        </div>
      </div>

      {!serverReady && (
        <div className="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Reminders are not fully available on this device yet.
        </div>
      )}

      {permission === "unsupported" && (
        <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          This browser does not support service workers or push notifications.
        </div>
      )}

      {error && <div className="mt-4 rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}
      {message && <div className="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{message}</div>}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={serverReady ? handleEnable : handlePrepareBrowserNotifications}
          disabled={actionLoading || isEnabled || permission === "unsupported"}
          className="rounded-2xl bg-brand-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-lagoon disabled:cursor-not-allowed disabled:opacity-60"
        >
          {actionLoading && !isEnabled ? "Preparing..." : serverReady ? "Enable reminders" : "Enable browser notifications"}
        </button>
        <button
          type="button"
          onClick={handleDisable}
          disabled={actionLoading || !isEnabled}
          className="rounded-2xl border border-slate-300 px-5 py-3 text-sm font-semibold text-brand-ink transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {actionLoading && isEnabled ? "Disabling..." : "Disable reminders"}
        </button>
      </div>
    </div>
  );
}
