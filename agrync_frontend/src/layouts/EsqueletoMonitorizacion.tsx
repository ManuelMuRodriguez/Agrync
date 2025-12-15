import { Outlet } from "react-router-dom";
import SeleccionTask from "../components/SeleccionTask";

export default function EsqueletoMonitorizacion() {

    return (
      <>
          <SeleccionTask/>
          <Outlet/>
      </>
    )
  }
  