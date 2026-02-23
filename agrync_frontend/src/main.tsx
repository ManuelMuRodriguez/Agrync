import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import "react-toastify/dist/ReactToastify.css";
import './index.css'
import './i18n'
import App from './App.tsx'
import { ToastContainer } from "react-toastify"

const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
    <App />
    <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={true}
        closeOnClick
        pauseOnHover={false}
        pauseOnFocusLoss={false}
      />
      </QueryClientProvider>
  </React.StrictMode>
);