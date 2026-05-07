import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./app/App";
import { AuthProvider } from "./contexts/AuthContext";
import "./index.css";
import { registerPushServiceWorker } from "./services/pushNotifications";

registerPushServiceWorker().catch(() => {
  // Ignore initial service worker registration failures and let the UI surface explicit push errors later.
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
