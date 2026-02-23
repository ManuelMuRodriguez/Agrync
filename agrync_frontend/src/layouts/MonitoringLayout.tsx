import { Outlet } from "react-router-dom";
import SeleccionTask from "../components/TaskSelection";

export default function EsqueletoMonitorizacion() {

    return (
      <>
          <SeleccionTask/>
          <Outlet/>
      </>
    )
  }
  