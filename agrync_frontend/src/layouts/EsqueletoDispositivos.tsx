import { Outlet } from "react-router-dom";
import SeleccionComunicacion from "../components/SeleccionComunicacion";


export default function EsqueletoDispositivos() {

    return (
      <>
          <SeleccionComunicacion/>
          <Outlet/>
      </>
    )
  }