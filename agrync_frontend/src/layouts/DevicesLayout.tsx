import { Outlet } from "react-router-dom";
import SeleccionComunicacion from "../components/CommunicationSelection";


export default function EsqueletoDispositivos() {

    return (
      <>
          <SeleccionComunicacion/>
          <Outlet/>
      </>
    )
  }