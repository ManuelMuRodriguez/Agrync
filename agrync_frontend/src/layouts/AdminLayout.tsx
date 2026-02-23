import { Navigate, Outlet } from "react-router-dom"
import SeccionesAdministracion from "../components/AdminSections"
import { useAuth } from "../hooks/useAuth"

export default function EsqueletoAdministracion() {

  const { data } = useAuth()


  if (!data) {
    return null
  }

  if (data.role !== "Administrador") {
    return <Navigate to="/dashboard" replace />
  }

    return (
      <>
        <div className="ml-5">
            <SeccionesAdministracion/>
            <Outlet />
        </div>
        
      </>
    )
  }
  