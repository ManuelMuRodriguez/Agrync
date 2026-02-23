import CambiarEmail from "../components/ChangeEmail";
import CambiarPassword from "../components/ChangePassword";


export default function Credenciales() {


    return (
    <div className="flex flex-col lg:flex-row space-y-12 lg:space-y-0">
        <CambiarPassword/>
        <CambiarEmail/>
    </div>
    )
  }
  