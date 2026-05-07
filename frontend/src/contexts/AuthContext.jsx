import { createContext, useEffect, useState } from "react";
import client from "../api/client";
import { clearTokens, getStoredTokens, storeTokens } from "../api/authStorage";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async () => {
    try {
      const response = await client.get("/auth/profile/");
      setUser(response.data);
    } catch (error) {
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const { access } = getStoredTokens();
    if (access) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials) => {
    const response = await client.post("/auth/login/", credentials);
    storeTokens(response.data);
    await fetchProfile();
    return response.data;
  };

  const register = async (payload) => {
    await client.post("/auth/register/", payload);
    return login({ email: payload.email, password: payload.password });
  };

  const logout = async () => {
    const { refresh } = getStoredTokens();
    try {
      if (refresh) {
        await client.post("/auth/logout/", { refresh });
      }
    } catch (error) {
      // Ignore logout transport issues so the local session is still cleared.
    } finally {
      clearTokens();
      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    refreshProfile: fetchProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
