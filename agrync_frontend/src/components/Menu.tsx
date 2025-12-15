import { Link, useLocation, useNavigate} from "react-router-dom";
import { LuLayoutDashboard } from "react-icons/lu";
import { VscGraphLine } from "react-icons/vsc";
import { IoSettingsOutline } from "react-icons/io5";
import { RiAdminLine } from "react-icons/ri";
import { RiLogoutBoxLine } from "react-icons/ri";
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { logout } from '../api/AuthAPI';
import { toast } from 'react-toastify';
import { Role } from "../types";


const tabs = [
    { name: 'Dashboard', href: '/dashboard', icon: LuLayoutDashboard },
    { name: 'Graphs', href: '/graficas', icon: VscGraphLine },
    { name: 'Configuration', href: '/configuracion/perfil', icon: IoSettingsOutline },
    { name: 'Administration', href: '/administracion/monitorizacion/modbus', icon: RiAdminLine },
]


type MenuProps = {
    role: Role;
};

export default function Menu({role}: MenuProps) {

    const queryClient = useQueryClient()
    const navigate = useNavigate()
    const location = useLocation()
    //const currentTab = tabs.filter(tab => tab.href === location.pathname)[0].href

    const {mutate} = useMutation({
    mutationFn: logout,
    onError: (error) => {
      toast.error(error.message, {
      closeButton: false,
      className: 'bg-error text-white'
      })
    },
    onSuccess: (data) => {
      localStorage.removeItem('ACCESS_TOKEN_AGRYNC')
      queryClient.invalidateQueries({ queryKey: ['userInfo'] })
      navigate("/login")
      toast.success(data, {
      closeButton: false,
      className: 'bg-right-green text-white'
      })
    }
    
  })


    const handleLogout = () => mutate()

    //const queryClient = useQueryClient()
    //const logout = () => {
    //    localStorage.removeItem('ACCESS_TOKEN_AGRYNC')
    //    queryClient.invalidateQueries({queryKey: ['userInfo']})
    //}


  const filteredTabs = tabs.filter(tab => {
    if (tab.name === 'Administration' && role !== 'Administrador') {
      return false;
    }
    return true;
  });

  return (

    <nav className='h-fit flex flex-col items-center justify-between flex-grow ' >

        <div className=''>



        {filteredTabs.map((tab) => (
                            <Link
                                key={tab.name}
                                to={tab.href}
                                className={`${location.pathname.split("/")[1] == tab.href.split("/")[1] ? 'bg-bg-selection': 'hover:bg-bg-hover transition duration-300'} w-65 text-xl text-text-green font-semibold flex items-center justify-center rounded-2xl h-17 `}
                            >
                                <tab.icon
                                    className='mr-2'
                                    aria-hidden="true"
                                />
                                <span>{tab.name}</span>
                            </Link>
                        ))}


        </div>

        <div className='mb-4'>

            <button
                key="cerrar-sesion"
                className=' w-65 text-xl text-text-green font-semibold flex items-center justify-center rounded-lg h-17  hover:bg-bg-hover transition duration-300'
                onClick={handleLogout}
            > <RiLogoutBoxLine className='mr-2'
            aria-hidden="true" />  Log out</button>

        </div>

    </nav>
  )
}
