import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { App } from "./App";
import { AuthProvider } from "./components/auth";
import { BrandProvider } from "./components/brand-provider";
import { ThemeProvider } from "./components/theme-provider";
import { About } from "./pages/About";
import { Home } from "./pages/Home";
import { Settings } from "./pages/Settings";
import "./index.css";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Root element #root not found");
createRoot(rootElement).render(
  <StrictMode>
    {/* ThemeProvider OUTERMOST — BrandProvider reads the active theme to pick light/dark tokens. */}
    <ThemeProvider>
      <BrandProvider>
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route element={<App />}>
                <Route path="/" element={<Home />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/about" element={<About />} />
              </Route>
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </BrandProvider>
    </ThemeProvider>
  </StrictMode>,
);
