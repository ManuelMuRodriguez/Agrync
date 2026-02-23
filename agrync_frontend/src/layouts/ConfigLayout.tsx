import { Outlet } from "react-router-dom"
import SeccionesConfiguracion from "../components/ConfigSections"

export default function EsqueletoConfiguracion() {

    return (
      <>
        <div className="ml-5">
            <SeccionesConfiguracion/>
            <Outlet />
        </div>
        
      </>
    )
  }
  